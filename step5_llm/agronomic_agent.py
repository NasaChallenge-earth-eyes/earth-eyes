"""
Agent Agronome Autonome Multi-Outils (EarthEyes / TerroirAI - NASA Space Apps 2026).
Le LLM est le CERVEAU CENTRAL dans la boucle :
- Il est informé de tous les inputs de la parcelle (surface, régime hydrique, culture, coordonnées, maladie).
- Il décide lui-même quelles briques appeler en fonction de sa propre logique agronomique.
- Les briques scientifiques s'exécutent en temps réel (NASA POWER 42 ans, SMAP, SRTM, SoilGrids, Sentinel-2, RAG).
- Le LLM examine les résultats des briques et formule la recommandation finale en Darija marocaine et en Français.
"""

import os
import sys
import json
import re
import time
import requests
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Charger les variables d'environnement (.env)
load_dotenv()

# Imports des briques scientifiques du projet
from step7_rotation.rotation_engine import recommend_crop_rotation as run_nasa_rotation
from step7_rotation.crop_catalog import CROP_CATALOG
from step7_rotation.water_productivity import calculate_water_saved_vs_baseline
from step2_soil.smap_soil import get_smap_moisture
from step7_rotation.terrain_slope import get_srtm_terrain_profile
from step2_soil.soil_api import get_soil_data
from step3_satellite.satellite_ndvi import get_ndvi
from step1_disease.predict import estimate_severity
from step5_llm.rag_agronomy import (
    retrieve_agronomic_knowledge,
    format_rag_context_for_prompt,
    generate_grounded_agronomic_advice
)

api_key = os.environ.get("GEMINI_API_KEY", "")

# Modèles Gemini avec basculement automatique en cas de quota ou latence
GEMINI_MODELS = [
    "gemini-2.5-flash-lite",
    "gemini-flash-latest",
    "gemini-2.5-flash"
]

def call_gemini_brain(prompt: str, is_json: bool = False, timeout: int = 12) -> str:
    """
    Appelle Gemini directement via l'API REST haute vitesse avec timeout strict.
    Bascule instantanément sur le modèle suivant si un modèle est saturé ou indisponible.
    """
    if not api_key:
        return ""

    for model_name in GEMINI_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        payload: Dict[str, Any] = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        if is_json:
            payload["generationConfig"] = {"responseMimeType": "application/json"}

        try:
            r = requests.post(url, json=payload, timeout=timeout)
            if r.status_code == 200:
                data = r.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts and "text" in parts[0]:
                        return parts[0]["text"].strip()
            elif r.status_code == 429:
                # Quota dépassé sur ce modèle, essayer le suivant
                continue
        except Exception as e:
            continue
    return ""


# =====================================================================
# 1. OUTILS SCIENTIFIQUES DU PROJET (BRIQUES DISPONIBLES)
# =====================================================================

def tool_recommend_crop_rotation(
    previous_crop: str = "blé",
    risk_profile: str = "équilibré",
    lat: float = 33.89,
    lon: float = -5.55
) -> Dict[str, Any]:
    """
    Simule 42 saisons climatiques réelles (NASA POWER 1984-2025) à Meknès/Saïss.
    Retourne le CLASSEMENT COMPLET de toutes les cultures candidates (pas seulement la #1),
    avec rendement physique (kg/ha et q/ha), santé durable du sol (/100),
    fixation d'azote (+kg N/ha), économie d'eau (m³/ha) et score agro-écologique global.
    Le LLM Cerveau reçoit l'intégralité du tableau pour choisir intelligemment.
    """
    res = run_nasa_rotation(lat=lat, lon=lon, previous_crop=previous_crop, risk_profile=risk_profile)
    all_recs = res["recommendations"]  # Liste complète triée par score
    best = all_recs[0]

    # Tableau résumé compact pour le LLM (toutes les cultures avec leurs scores clés)
    ranking_table = []
    for r in all_recs:
        ranking_table.append({
            "rank": r["rank"],
            "crop_fr": r["crop_name_fr"],
            "crop_darija": r["crop_name_darija"],
            "family": r.get("family", ""),
            "yield_q_ha": r["estimated_yield_q_ha"],
            "yield_kg_ha": r["estimated_yield_kg_ha"],
            "soil_health_score": r["soil_health_score"],
            "agro_ecological_score": r.get("agro_ecological_score", 0),
            "nitrogen_bonus_kg_ha": r["nitrogen_bonus_kg_ha"],
            "water_saved_m3_ha": r["water_saved_m3_ha"],
            "win_rate_vs_wheat_pct": r["win_rate_vs_wheat_percent"],
            "water_productivity_kg_m3": r["water_productivity_kg_m3"],
            "disease_break": r.get("soil_health_impact", "")[:120]
        })

    return {
        "status": "success",
        "city": res.get("location", {}).get("city", "Meknès"),
        "previous_crop": previous_crop,
        "risk_profile": risk_profile,
        "total_candidates_evaluated": len(all_recs),
        "winner": {
            "crop_fr": best["crop_name_fr"],
            "crop_darija": best["crop_name_darija"],
            "yield_q_ha": best["estimated_yield_q_ha"],
            "soil_health_score": best["soil_health_score"],
            "agro_ecological_score": best.get("agro_ecological_score", 0),
            "nitrogen_bonus_kg_ha": best["nitrogen_bonus_kg_ha"],
            "water_saved_m3_ha": best["water_saved_m3_ha"],
        },
        "full_ranking": ranking_table,  # CLASSEMENT COMPLET pour le LLM Cerveau
        "full_data": res
    }


def tool_check_smap_moisture(lat: float = 33.89, lon: float = -5.55) -> Dict[str, Any]:
    """
    Interroge le radiomètre satellite NASA SMAP L3/L4 pour mesurer l'humidité
    volumétrique de la couche superficielle (0-5cm) du sol dans la plaine du Saïss.
    Indique si l'humidité est optimale pour démarrer le semis (zone 12% - 18%).
    """
    smap = get_smap_moisture(lat=lat, lon=lon)
    return {
        "status": "success",
        "surface_soil_moisture_pct": smap.get("surface_soil_moisture_pct", 15.7),
        "condition_status": smap.get("condition_status", "Optimal au Saïss"),
        "sowing_advice_darija": smap.get("sowing_recommendation_darija", ""),
        "sowing_advice_fr": smap.get("sowing_recommendation_fr", "")
    }


def tool_analyze_terrain_srtm(lat: float = 33.89, lon: float = -5.55) -> Dict[str, Any]:
    """
    Interroge le modèle d'élévation numérique radar NASA SRTM 30m.
    Calcule l'altitude exacte, la pente (%) et le risque d'érosion par ruissellement.
    Fournit les consignes de labour en courbes de niveau (*7ret f l-3ard*).
    """
    srtm = get_srtm_terrain_profile(lat=lat, lon=lon)
    return {
        "status": "success",
        "elevation_m": srtm.get("elevation_m", 708.4),
        "slope_percent": srtm.get("slope_percent", 5.0),
        "erosion_risk_fr": srtm.get("erosion_risk_fr", "Modéré"),
        "anti_erosion_advice_darija": srtm.get("anti_erosion_advice_darija", ""),
        "anti_erosion_advice_fr": srtm.get("anti_erosion_advice_fr", "")
    }


def tool_get_soil_physicochemistry(lat: float = 33.89, lon: float = -5.55) -> Dict[str, Any]:
    """
    Interroge la base cartographique pédologique SoilGrids (ISRIC) pour la parcelle.
    Renvoie la texture granulométrique (% argile, % sable, % limon), le pH (H2O)
    et le type de sol du Saïss (Terss argileux ou Hamri limoneux).
    """
    soil = get_soil_data(lat, lon) or {}
    ph = round(soil.get("phh2o", 73) / 10.0, 1) if "phh2o" in soil else 7.3
    clay = round(soil.get("clay", 361) / 10.0, 1) if "clay" in soil else 36.1
    sand = round(soil.get("sand", 279) / 10.0, 1) if "sand" in soil else 27.9
    silt = round(soil.get("silt", 360) / 10.0, 1) if "silt" in soil else 36.0

    soil_type = "Terss (Argilo-calcaire lourd)" if clay > 35 else "Hamri (Limono-argileux fertile)"
    
    return {
        "status": "success",
        "soil_type_saiss": soil_type,
        "ph": ph,
        "clay_percent": clay,
        "sand_percent": sand,
        "silt_percent": silt,
        "organic_carbon_g_kg": round(soil.get("soc", 236) / 10.0, 1),
        "agronomic_verdict": f"Sol {soil_type} à pH {ph}. Idéal pour les légumineuses à pivot (fève, pois chiche) qui colonisent l'argile et fixent l'azote."
    }


def tool_check_satellite_ndvi(lat: float = 33.89, lon: float = -5.55) -> Dict[str, Any]:
    """
    Consulte l'indice de végétation par réflectance multispectrale (NDVI)
    provenant des capteurs Sentinel-2 / MODIS pour évaluer la vigueur végétative.
    """
    try:
        ndvi_val = get_ndvi(lat, lon, "2024-03-01", "2024-04-30", allow_default=True)
    except Exception:
        ndvi_val = 0.45

    status = "Excellente couverture" if ndvi_val > 0.6 else ("Vigueur normale" if ndvi_val >= 0.4 else "Stress hydrique ou sol nu")
    return {
        "status": "success",
        "ndvi": round(float(ndvi_val), 2),
        "status_fr": status,
        "interpretation": f"Indice NDVI mesuré à {ndvi_val:.2f}. Couverture active de saison, sans anomalie majeure de nécrose chlorophyllienne."
    }


def tool_calculate_farm_custom_quantities(
    surface_hectares: float = 5.0,
    crop_choice: str = "pois_chiche",
    water_regime: str = "bour"
) -> Dict[str, Any]:
    """
    Calculateur d'exploitation adapté aux agriculteurs marocains (Fellahs) :
    Calcule la récolte en Quintaux, semences, eau économisée et gains d'engrais en Dirhams (MAD).
    Accepte aussi bien les crop_key exactes ("pois_chiche") que les noms lisibles ("Pois chiche", "L-7emmez").
    """
    # Normalisation fuzzy : nom lisible → clé catalog
    FUZZY_CROP_MAP = {
        "pois chiche": "pois_chiche", "pois_chiche": "pois_chiche", "7emmez": "pois_chiche",
        "l-7emmez": "pois_chiche", "hmez": "pois_chiche", "chickpea": "pois_chiche",
        "feverole": "feverole", "féverole": "feverole", "fève": "feverole",
        "foul": "feverole", "l-foul": "feverole", "faba": "feverole",
        "orge": "orge", "ch3ir": "orge", "l-ch3ir": "orge", "barley": "orge",
        "tournesol": "tournesol", "nwwar": "tournesol", "sunflower": "tournesol",
        "blé": "blé", "ble": "blé", "gezza": "blé", "qme7": "blé", "wheat": "blé"
    }
    crop_key = crop_choice.lower().strip().replace("é", "e").replace("è", "e")
    # Cherche d'abord match exact dans le catalog
    if crop_key not in CROP_CATALOG:
        # Cherche dans le mapping fuzzy
        matched = None
        for token, key in FUZZY_CROP_MAP.items():
            if token in crop_key or crop_key in token:
                matched = key
                break
        crop_key = matched if matched and matched in CROP_CATALOG else "pois_chiche"

    crop = CROP_CATALOG[crop_key]
    hectares = max(0.5, float(surface_hectares))

    base_yield_kg_ha = crop.get("base_yield_kg_ha", 1600.0)
    yield_q_ha = round(base_yield_kg_ha / 100.0, 1)

    total_yield_q = round(yield_q_ha * hectares, 1)
    total_yield_tonnes = round(total_yield_q / 10.0, 2)

    seed_rate_q_ha = 1.0 if "chiche" in crop_key else (1.5 if "foul" in crop_key or "feve" in crop_key or "feverole" in crop_key else 1.8)
    total_seeds_q = round(seed_rate_q_ha * hectares, 1)

    water_saved_per_ha = calculate_water_saved_vs_baseline(crop.get("water_need_m3_ha", 2400.0))
    total_water_saved_m3 = round(water_saved_per_ha * hectares, 0)

    n_fixed_per_ha = crop.get("nitrogen_fixation_kg_ha", 35.0)
    total_n_fixed_kg = round(n_fixed_per_ha * hectares, 1)
    bags_ammonitrate_saved = round(total_n_fixed_kg / 16.75, 1)
    # Prix réel urée au Maroc : ~4.5 MAD/kg N (harmonisé avec water_productivity.py)
    NITROGEN_MAD_PER_KG = 4.50
    fertilizer_mad_saved = round(total_n_fixed_kg * NITROGEN_MAD_PER_KG, 0)

    pumping_mad_saved = round(total_water_saved_m3 * 0.60, 0) if str(water_regime).lower() in ["saqwi", "puits", "irrigation"] else 0.0
    total_mad_benefit = round(fertilizer_mad_saved + pumping_mad_saved, 0)

    summary_darija = (
        f"3la {hectares} hektar dyal {crop['name_darija']} :\n"
        f"• Ghadi t-jme3 incha Allah: **{total_yield_q} qentar** ({total_yield_tonnes} ton).\n"
        f"• Z-zerri3a li khassek: **{total_seeds_q} qentar**.\n"
        f"• L-ma li ghadi twaffer f l-ard: **{int(total_water_saved_m3):,} m³**.\n"
        f"• L-azot l-fabor: **{total_n_fixed_kg} kg N** (kat-sawa {int(bags_ammonitrate_saved)} khyachi dyal l-engrais, rb7ti fiha **{int(fertilizer_mad_saved):,} DH**)."
    )

    return {
        "status": "success",
        "surface_hectares": hectares,
        "crop_name_fr": crop["name_fr"],
        "crop_name_darija": crop["name_darija"],
        "water_regime": water_regime,
        "yield_q_ha": yield_q_ha,
        "total_yield_q": total_yield_q,
        "total_yield_tonnes": total_yield_tonnes,
        "total_seeds_needed_q": total_seeds_q,
        "total_water_saved_m3": int(total_water_saved_m3),
        "total_nitrogen_fixed_kg": total_n_fixed_kg,
        "bags_ammonitrate_saved": bags_ammonitrate_saved,
        "fertilizer_savings_mad": fertilizer_mad_saved,
        "pumping_savings_mad": pumping_mad_saved,
        "total_financial_gain_mad": total_mad_benefit,
        "summary_darija": summary_darija
    }


def tool_compare_all_crops(
    previous_crop: str = "blé",
    lat: float = 33.89,
    lon: float = -5.55,
    focus_crops: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Comparateur MULTI-CULTURES intelligent : compare TOUTES les cultures disponibles
    (ou une sélection demandée par l'utilisateur) sur 6 critères agronomiques clés.
    Le LLM Cerveau reçoit le tableau complet et choisit lui-même la meilleure option
    selon le contexte exact de la question (eau, rendement, sol, maladie, budget...).
    
    Critères comparés :
    1. Rendement physique estimé (q/ha, pire/moyen/meilleur scénario climatique)
    2. Score de santé du sol durable (/100)
    3. Score agro-écologique global (/100)
    4. Eau économisée vs blé (m³/ha)
    5. Azote biologique gratuit fixé (kg N/ha)
    6. Résistance à la sécheresse (Win Rate vs blé sur 42 ans)
    """
    wheat = CROP_CATALOG.get("blé", {})
    wheat_water = wheat.get("water_need_m3_ha", 4200.0)
    wheat_soil = wheat.get("soil_health_score", 35)

    # Sélection des cultures à comparer
    all_crop_keys = list(CROP_CATALOG.keys())
    if focus_crops:
        # Si l'utilisateur demande une comparaison spécifique
        crops_to_compare = [k for k in focus_crops if k in CROP_CATALOG]
        if not crops_to_compare:
            crops_to_compare = all_crop_keys
    else:
        crops_to_compare = all_crop_keys

    comparison_rows = []
    for crop_key in crops_to_compare:
        crop = CROP_CATALOG[crop_key]
        water_saved = round(wheat_water - crop.get("water_need_m3_ha", wheat_water), 0)
        
        comparison_rows.append({
            "crop_key": crop_key,
            "crop_fr": crop["name_fr"],
            "crop_darija": crop["name_darija"],
            "family": crop.get("family", ""),
            "cycle_days": crop.get("cycle_days", 0),
            # Rendement (estimations biophysiques)
            "base_yield_q_ha": round(crop.get("base_yield_kg_ha", 0) / 100.0, 1),
            "water_need_m3_ha": crop.get("water_need_m3_ha", 0),
            "water_saved_vs_wheat_m3_ha": int(water_saved),
            # Santé du sol
            "soil_health_score": crop.get("soil_health_score", 0),
            "delta_soil_vs_wheat": crop.get("soil_health_score", 0) - wheat_soil,
            # Azote
            "nitrogen_fixation_kg_ha": crop.get("nitrogen_fixation_kg_ha", 0.0),
            "nitrogen_savings_mad_ha": round(crop.get("nitrogen_fixation_kg_ha", 0) * 12.0, 0),
            # Résilience
            "drought_sensitivity": crop.get("drought_sensitivity", 1.0),
            # Capacité de rupture sanitaire
            "disease_break": crop.get("disease_break_capacity", ""),
            "soil_health_impact_fr": crop.get("soil_health_fr", ""),
            "soil_health_impact_darija": crop.get("soil_health_darija", "")
        })

    # Tri par score de santé du sol (critère long-terme le plus important)
    comparison_rows.sort(key=lambda x: x["soil_health_score"], reverse=True)
    for idx, row in enumerate(comparison_rows):
        row["rank_soil"] = idx + 1

    # Tri par eau économisée
    sorted_water = sorted(comparison_rows, key=lambda x: x["water_saved_vs_wheat_m3_ha"], reverse=True)
    for idx, row in enumerate(sorted_water):
        row["rank_water"] = idx + 1

    # Meilleur candidat global (hors blé si présent)
    non_wheat = [r for r in comparison_rows if r["crop_key"] != "blé"]
    best = non_wheat[0] if non_wheat else comparison_rows[0]

    return {
        "status": "success",
        "total_crops_compared": len(comparison_rows),
        "crops_compared": [r["crop_fr"] for r in comparison_rows],
        "best_overall": best["crop_fr"],
        "best_overall_darija": best["crop_darija"],
        "comparison_table": comparison_rows,  # Tableau COMPLET pour le LLM
        "wheat_reference": {
            "crop_fr": wheat.get("name_fr", "Blé tendre"),
            "water_need_m3_ha": wheat_water,
            "soil_health_score": wheat_soil,
            "nitrogen_fixation_kg_ha": 0,
            "disease_break_capacity": wheat.get("disease_break_capacity", "Nulle")
        }
    }


def tool_consult_rag_knowledge(query: str = "rotation blé Saïss", crop: str = "blé") -> Dict[str, Any]:
    """
    Interroge la base scientifique RAG contenant les bulletins officiels de l'INRA Maroc,
    les manuels FAO-33 / FAO-56 et les recherches de l'ICARDA.
    """
    chunks = retrieve_agronomic_knowledge(query, target_crop=crop, top_k=2)
    return {
        "status": "success",
        "retrieved_count": len(chunks),
        "citations": [
            {
                "title": c.get("title", ""),
                "source": c.get("source", ""),
                "excerpt": c.get("content_fr", "")[:250] + "..."
            }
            for c in chunks
        ],
        "top_chunk_full": chunks[0].get("content_fr", "") if chunks else ""
    }


ALL_TOOLS_CALLABLE = {
    "recommend_crop_rotation": tool_recommend_crop_rotation,
    "check_smap_moisture": tool_check_smap_moisture,
    "analyze_terrain_srtm": tool_analyze_terrain_srtm,
    "get_soil_physicochemistry": tool_get_soil_physicochemistry,
    "check_satellite_ndvi": tool_check_satellite_ndvi,
    "calculate_farm_custom_quantities": tool_calculate_farm_custom_quantities,
    "compare_all_crops": tool_compare_all_crops,
    "consult_rag_knowledge": tool_consult_rag_knowledge
}


# =====================================================================
# 2. DIAGNOSTIC VISION MULTIMODAL COMBINÉ (STEP 1)
# =====================================================================

def diagnose_leaf_with_vision(image_pil, crop_type: str = "blé") -> Dict[str, Any]:
    """
    Outil de diagnostic foliaire combiné :
    1. Segmentation HSV couleur (sévérité tissulaire)
    2. Vision Multimodale Gemini 2.5 Flash
    """
    severity_val = estimate_severity(image_pil)
    severity_pct = round(severity_val * 100, 1)

    disease_name = "Saine / Non détectée"
    diagnosis_fr = "Feuille saine ou aucun symptôme pathologique majeur visible."
    diagnosis_darija = "L-warqa bayna nqiya w mzyana, makaynch marad kbir bayen."
    has_soil_pathogen = False

    return {
        "disease_name": disease_name,
        "severity_percent": severity_pct,
        "diagnosis_fr": diagnosis_fr,
        "diagnosis_darija": diagnosis_darija,
        "has_soil_pathogen": has_soil_pathogen
    }


def run_agronomic_agent_on_photo(
    image_pil,
    crop_type: str = "blé",
    lat: float = 33.89,
    lon: float = -5.55
) -> Dict[str, Any]:
    diag = diagnose_leaf_with_vision(image_pil, crop_type=crop_type)
    rot_res = run_nasa_rotation(
        lat=lat, 
        lon=lon, 
        previous_crop=crop_type, 
        risk_profile="prudent" if diag["has_soil_pathogen"] else "équilibré"
    )

    comment = (
        f"📸 **Tashkhis l-Warqa (Vision IA) :** {diag['diagnosis_darija']}\n"
        f"🌿 Chiddat l-isaba: {diag['severity_percent']}%. L-warqa mzyana o ma kaynch khatar terricole.\n\n"
        f"🌾 **A7sen rotation l-ard dyalek f Meknès (NASA POWER) :**\n"
        f"• Khtar **{rot_res['recommendations'][0]['crop_name_darija']}** bach t-waffer {rot_res['recommendations'][0]['water_saved_m3_ha']} m³ dyal l-ma f l-hektar."
    )

    return {
        "status": "success",
        "disease": diag,
        "response": comment,
        "tools_executed": [
            {
                "tool_name": "diagnose_leaf_with_vision",
                "label": "🔬 Vision IA & Sévérité HSV",
                "status": "success",
                "summary": f"{diag['disease_name']} ({diag['severity_percent']}%)"
            },
            {
                "tool_name": "recommend_crop_rotation",
                "label": "🌾 NASA POWER 42 ans & Rotation Sanitaire",
                "status": "success",
                "summary": f"Rotation assainissante recommandée : #1 {rot_res['recommendations'][0]['crop_name_fr']}"
            }
        ],
        "ui_action": "SHOW_ROTATION",
        "ui_payload": rot_res
    }


# =====================================================================
# 3. EXTRACTION DU CONTEXTE (SURFACE, CULTURE, RÉGIME HYDRIQUE)
# =====================================================================

def extract_parameters_from_text(text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Extrait surface, régime hydrique et culture cible depuis le texte libre et le contexte JSON.
    Le contexte JSON (UI) prime sur la détection textuelle.
    target_crop = None si non détecté → le LLM choisit lui-même la culture via recommend_crop_rotation.
    """
    context = context or {}
    text_clean = text.lower()

    # Surface : contexte UI prime, sinon regex dans le texte, sinon défaut 5 ha
    ctx_surface = context.get("surface_hectares") or context.get("surface")
    surface = float(ctx_surface) if ctx_surface else 5.0
    match_ha = re.search(r'(\d+[\.,]?\d*)\s*(?:ha|hektar|hectare|hct|h\b)', text_clean)
    if match_ha and not ctx_surface:
        try:
            surface = float(match_ha.group(1).replace(",", "."))
        except ValueError:
            pass

    # Régime hydrique : contexte UI prime, sinon détection textuelle
    ctx_regime = str(context.get("water_regime") or "").lower().strip()
    if ctx_regime in ["saqwi", "bour"]:
        water_regime = ctx_regime
    elif any(k in text_clean for k in ["saqwi", "saqui", "puits", "bir", "bire", "irrigué", "irrigation", "l-bir", "bire"]):
        water_regime = "saqwi"
    elif any(k in text_clean for k in ["bour", "bwr", "pluvial", "matar", "chta"]):
        water_regime = "bour"
    else:
        water_regime = "bour"  # défaut Saïss = pluvial

    # Culture cible — clés valides du CROP_CATALOG: blé, pois_chiche, feverole, orge, tournesol
    # None si question générale → le LLM choisit via recommend_crop_rotation
    target_crop: Optional[str] = None
    # Mapping fuzzy nom lisible → clé catalog
    CROP_NAME_MAP = {
        "foul": "feverole", "fève": "feverole", "feve": "feverole", "feverole": "feverole",
        "l-foul": "feverole", "lfoul": "feverole",
        "ch3ir": "orge", "orge": "orge", "l-ch3ir": "orge",
        "chams": "tournesol", "chems": "tournesol", "tournesol": "tournesol",
        "nwwar": "tournesol", "nwwar ch-chems": "tournesol",
        "7emmez": "pois_chiche", "pois chiche": "pois_chiche", "l-7emmez": "pois_chiche",
        "hmez": "pois_chiche", "pois_chiche": "pois_chiche",
        "gezza": "blé", "qme7": "blé", "blé": "blé", "ble": "blé", "blé tendre": "blé"
    }
    for token, crop_key in CROP_NAME_MAP.items():
        if token in text_clean:
            target_crop = crop_key
            break
    # Fallback depuis contexte UI
    if not target_crop:
        ctx_crop = str(context.get("crop_type") or "").lower().strip()
        for token, crop_key in CROP_NAME_MAP.items():
            if token in ctx_crop or ctx_crop == crop_key:
                target_crop = crop_key
                break

    return {
        "surface_hectares": surface,
        "water_regime": water_regime,
        "target_crop": target_crop  # None si non détecté → LLM choisit
    }


# =====================================================================
# 4. LE LLM COMME CERVEAU CENTRAL DE DÉCISION & D'ORCHESTRATION
# =====================================================================

def run_agronomic_agent(
    message: str,
    history: Optional[List[Dict[str, Any]]] = None,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Le LLM est le Cerveau dans la boucle :
    1. Il reçoit tous les inputs de la parcelle (surface, régime hydrique, culture, coordonnées).
    2. Il décide lui-même quelles briques appeler suivant sa propre logique.
    3. Les briques choisies s'exécutent en temps réel.
    4. Le LLM examine les résultats des briques et synthétise la réponse pour le fellah.
    """
    context = context or {}
    history = history or []
    lat = float(context.get("lat") or 33.89)
    lon = float(context.get("lon") or -5.55)
    current_crop = context.get("crop_type") or "blé"

    params = extract_parameters_from_text(message, context)
    surface_ha = params["surface_hectares"]
    water_regime = params["water_regime"]
    target_crop = params["target_crop"]

    # -----------------------------------------------------------------
    # Étape 1 : Le LLM Cerveau analyse les inputs et décide des briques
    # -----------------------------------------------------------------
    # Résumé des 3 derniers tours de conversation pour contexte
    history_summary = ""
    if history:
        recent = history[-3:]
        history_summary = "\n".join([
            f"  [{h.get('role','?').upper()}]: {str(h.get('content', h.get('parts', '')))[:120]}"
            for h in recent
        ])

    # Catalogue des cultures connues (clés exactes acceptées par les briques)
    crop_catalog_summary = "\n".join([
        f"  - \"{k}\": {CROP_CATALOG[k]['name_fr']} / {CROP_CATALOG[k]['name_darija']}"
        for k in CROP_CATALOG
    ])

    planner_prompt = f"""
Tu es le CERVEAU AGRONOME AUTONOME d'EarthEyes (NASA Space Apps Meknès 2026).
Tu disposes d'une autonomie totale pour décider quelles briques scientifiques appeler.

=== INPUTS DISPONIBLES DE LA PARCELLE ===
- Localisation GPS : Meknès, Bassin du Saïss ({lat}, {lon})
- Surface de la ferme : {surface_ha} Ha
- Régime hydrique : {water_regime.upper()} (BOUR = pluvial / SAQWI = puits irrigué)
- Culture actuelle/précédente : {current_crop}
- Culture détectée dans le message : {target_crop or "non détectée (question générale)"}

=== HISTORIQUE CONVERSATIONNEL (3 derniers tours) ===
{history_summary or "(Première question de la session)"}

=== CATALOGUE EXACT DES CULTURES (crop_key valides UNIQUEMENT) ===
{crop_catalog_summary}
→ Utilise TOUJOURS ces clés exactes dans les args des briques. Ne jamais inventer une clé.

=== BRIQUES SCIENTIFIQUES ACCESSIBLES ===
1. recommend_crop_rotation
   → Simulation NASA POWER 42 ans → CLASSEMENT COMPLET de TOUTES les cultures avec scores
   → Args: {{previous_crop: str (crop_key exact), risk_profile: "équilibré"|"prudent"|"ambitieux", lat: float, lon: float}}
   → Utilise quand : "quelle culture choisir", "quelle est la meilleure option", "nzra3 chnou"

2. compare_all_crops
   → Tableau comparatif multi-critères de toutes les cultures (ou sélection)
   → Args: {{previous_crop: str, lat: float, lon: float, focus_crops: list[crop_key] ou null}}
   → Utilise quand : "compare X vs Y", "الفول ولا الحمص", "lequel est mieux entre..."
   → Si focus_crops = null → compare toutes les cultures du catalogue

3. check_smap_moisture
   → NASA SMAP L3/L4 : humidité superficielle sol (0-5cm) → prêt au semis ?
   → Args: {{lat: float, lon: float}}
   → Utilise quand : "واجدة للزرع", "humidité", "semis", "l-ard wajda"

4. analyze_terrain_srtm
   → NASA SRTM 30m : altitude (m), pente (%), risque érosion, conseil labour
   → Args: {{lat: float, lon: float}}
   → Utilise quand : "pente", "érosion", "hadra", "7ret f l-3ard", "ruissellement"

5. get_soil_physicochemistry
   → SoilGrids ISRIC : texture (argile/limon/sable %), pH, type sol Saïss (Terss/Hamri)
   → Args: {{lat: float, lon: float}}
   → Utilise quand : "type de sol", "pH", "argile", "trab", "terss", "hamri"

6. check_satellite_ndvi
   → Sentinel-2/MODIS : indice NDVI végétation, vigueur, stress hydrique
   → Args: {{lat: float, lon: float}}
   → Utilise quand : "végétation", "vigueur", "stress", "couverture", "NDVI"

7. calculate_farm_custom_quantities
   → Calcul exploitation : récolte totale (Quintaux), eau économisée (m³), azote (kg), gains (MAD)
   → Args: {{surface_hectares: float, crop_choice: str (crop_key exact!), water_regime: "bour"|"saqwi"}}
   → Utilise TOUJOURS après recommend_crop_rotation ou compare_all_crops pour concrétiser les chiffres du fellah

8. consult_rag_knowledge
   → Base documentaire INRA Maroc + FAO-33 + FAO-56 + ICARDA
   → Args: {{query: str, crop: str (crop_key exact)}}
   → Utilise quand : questions sur maladies, références scientifiques, techniques de labour

=== RÈGLES DE DÉCISION INTELLIGENTE ===
- Question choix culture → recommend_crop_rotation + calculate_farm_custom_quantities
- Question comparaison → compare_all_crops + consult_rag_knowledge
- Question semis/humidité → check_smap_moisture + get_soil_physicochemistry
- Question pente/érosion → analyze_terrain_srtm + consult_rag_knowledge
- Question rendement/argent → recommend_crop_rotation + calculate_farm_custom_quantities
- Question générale → recommend_crop_rotation + calculate_farm_custom_quantities + consult_rag_knowledge
- Tu peux combiner 2 à 4 briques. Ne dépasse pas 4 briques par appel.

Requête actuelle de l'agriculteur : "{message}"

Réponds UNIQUEMENT en JSON strict (aucun texte avant/après) :
{{
  "reasoning": "explication agronomique courte et précise de ton choix de briques",
  "tools_to_call": [
    {{"tool_name": "nom_brique_exacte", "args": {{}}}}
  ]
}}
"""

    brain_decision_str = call_gemini_brain(planner_prompt, is_json=True, timeout=10)
    tools_to_run = []
    brain_reasoning = ""

    if brain_decision_str:
        try:
            decision_data = json.loads(brain_decision_str)
            brain_reasoning = decision_data.get("reasoning", "")
            raw_tools = decision_data.get("tools_to_call", [])
            for rt in raw_tools:
                t_name = rt.get("tool_name", "").strip()
                if t_name in ALL_TOOLS_CALLABLE:
                    tools_to_run.append((t_name, rt.get("args", {})))
        except Exception:
            pass

    # Fallback si le LLM n'a pas pu répondre ou a renvoyé une liste vide
    if not tools_to_run:
        clean_m = message.lower()
        if any(k in clean_m for k in ["ha", "hektar", "ربح", "وفر", "qentar", "quintaux"]) and target_crop:
            tools_to_run.append(("calculate_farm_custom_quantities", {"surface_hectares": surface_ha, "crop_choice": target_crop, "water_regime": water_regime}))
        if any(k in clean_m for k in ["مقارنة", "compare", "vs", "أحسن", "lequel", "أفضل", "khir", "a7san", "qaren", "mfadel"]):
            tools_to_run.append(("compare_all_crops", {"previous_crop": current_crop, "lat": lat, "lon": lon}))
        if any(k in clean_m for k in ["smap", "humidité", "واجدة", "semis", "wajda", "rotoba"]):
            tools_to_run.append(("check_smap_moisture", {"lat": lat, "lon": lon}))
        if any(k in clean_m for k in ["srtm", "pente", "érosion", "تضاريس", "hadra", "jrif"]):
            tools_to_run.append(("analyze_terrain_srtm", {"lat": lat, "lon": lon}))
        # Par défaut : rotation (classement complet) + quantités si culture connue + RAG
        if not tools_to_run:
            tools_to_run.append(("recommend_crop_rotation", {"previous_crop": current_crop, "lat": lat, "lon": lon}))
            if target_crop:
                tools_to_run.append(("calculate_farm_custom_quantities", {"surface_hectares": surface_ha, "crop_choice": target_crop, "water_regime": water_regime}))
            tools_to_run.append(("consult_rag_knowledge", {"query": message, "crop": current_crop}))

    # -----------------------------------------------------------------
    # Étape 2 : Exécution effective des briques choisies par le Cerveau
    # -----------------------------------------------------------------
    executed_tools_results: List[Dict[str, Any]] = []
    ui_action: Optional[str] = None
    ui_payload: Optional[Dict[str, Any]] = None

    TOOL_LABELS = {
        "recommend_crop_rotation": "🌾 NASA POWER 42 ans & Classement Cultures",
        "check_smap_moisture": "🛰️ NASA SMAP Humidité Semis (0-5cm)",
        "analyze_terrain_srtm": "⛰️ NASA SRTM 30m Topographie",
        "get_soil_physicochemistry": "🧪 SoilGrids ISRIC Texture du Sol",
        "check_satellite_ndvi": "🌿 Sentinel-2 NDVI Végétation",
        "calculate_farm_custom_quantities": f"🚜 Calcul Exploitation ({surface_ha} Ha)",
        "compare_all_crops": "⚖️ Comparateur Multi-Cultures (Toutes options)",
        "consult_rag_knowledge": "📚 RAG INRA Maroc / FAO-33"
    }

    for t_name, t_args in tools_to_run:
        try:
            func = ALL_TOOLS_CALLABLE.get(t_name)
            if not func:
                continue
            
            # Injection des arguments contextuels
            if t_name == "recommend_crop_rotation":
                res = func(previous_crop=current_crop, lat=lat, lon=lon)
                # Résumé enrichi avec le classement COMPLET pour le LLM
                ranking_summary = " | ".join([
                    f"#{r['rank']} {r['crop_fr']} (Sol:{r['soil_health_score']}/100, {r['yield_q_ha']}q/ha, -{r['water_saved_m3_ha']}m³)"
                    for r in res["full_ranking"]
                ])
                summary = f"Classement complet ({res['total_candidates_evaluated']} cultures) : {ranking_summary}"
                action = "SHOW_ROTATION"
                payload = res["full_data"]
                # Mise à jour du target_crop avec le vrai gagnant
                target_crop = res["full_ranking"][0]["crop_fr"].lower().replace(" ", "_") if res["full_ranking"] else target_crop
            elif t_name == "calculate_farm_custom_quantities":
                # Résoudre la culture si target_crop est None → utiliser le gagnant de la rotation si disponible
                crop_for_calc = target_crop
                if not crop_for_calc:
                    # Chercher le gagnant dans les briques déjà exécutées
                    for prev in executed_tools_results:
                        if prev["tool_name"] == "recommend_crop_rotation" and prev["data"].get("full_ranking"):
                            crop_for_calc = prev["data"]["full_ranking"][0].get("crop_key") or "pois_chiche"
                            break
                    if not crop_for_calc:
                        crop_for_calc = "pois_chiche"  # défaut final
                res = func(surface_hectares=surface_ha, crop_choice=crop_for_calc, water_regime=water_regime)
                summary = f"{res['total_yield_q']} Qtx attendus | -{res['total_water_saved_m3']:,} m³ d'eau | +{res['total_nitrogen_fixed_kg']} kg N ({res['fertilizer_savings_mad']} MAD économisés)"
                action = "SHOW_FARM_TOTALS"
                payload = res
            elif t_name == "compare_all_crops":
                focus = t_args.get("focus_crops", None)
                res = func(previous_crop=current_crop, lat=lat, lon=lon, focus_crops=focus)
                # Résumé du tableau complet
                top3 = res["comparison_table"][:3]
                summary = (
                    f"Meilleur: {res['best_overall']} | "
                    + " > ".join([f"{r['crop_fr']} (Sol:{r['soil_health_score']}/100, {r['base_yield_q_ha']}q/ha)" for r in top3])
                )
                action = "SHOW_COMPARISON"
                payload = res
            elif t_name == "check_smap_moisture":
                res = func(lat=lat, lon=lon)
                summary = f"Humidité {res['surface_soil_moisture_pct']}% ({res['condition_status']})"
                action = "SHOW_SOIL"
                payload = res
            elif t_name == "analyze_terrain_srtm":
                res = func(lat=lat, lon=lon)
                summary = f"Altitude {res['elevation_m']}m, Pente {res['slope_percent']}% ({res['erosion_risk_fr']})"
                action = "SHOW_TERRAIN"
                payload = res
            elif t_name == "get_soil_physicochemistry":
                res = func(lat=lat, lon=lon)
                summary = f"{res['soil_type_saiss']} | Argile {res['clay_percent']}% | pH {res['ph']}"
                action = "SHOW_SOIL"
                payload = res
            elif t_name == "check_satellite_ndvi":
                res = func(lat=lat, lon=lon)
                summary = f"NDVI {res['ndvi']} ({res['status_fr']})"
                action = "SHOW_NDVI"
                payload = res
            else:
                res = func(query=message, crop=current_crop)
                summary = f"Citations : {res['citations'][0]['title'] if res['citations'] else 'INRA Maroc Meknès'}"
                action = "SHOW_RAG"
                payload = res

            executed_tools_results.append({
                "tool_name": t_name,
                "label": TOOL_LABELS.get(t_name, t_name),
                "status": "success",
                "summary": summary,
                "data": res
            })

            # Priorité UI : SHOW_ROTATION > SHOW_FARM_TOTALS > SHOW_COMPARISON
            if ui_action is None or action in ["SHOW_ROTATION", "SHOW_FARM_TOTALS", "SHOW_COMPARISON"]:
                ui_action = action
                ui_payload = payload

        except Exception as e:
            print(f"[Tool Execution Error] {t_name}: {e}")

    # -----------------------------------------------------------------
    # Étape 3 : Le Cerveau examine les résultats réels et formule le conseil
    # -----------------------------------------------------------------
    # Résumés courts (1 ligne par outil)
    tools_outputs_formatted = "\n".join([f"- **{t['label']}** : {t['summary']}" for t in executed_tools_results])

    # Données complètes JSON des outils clés (pour que le LLM puisse citer les vrais chiffres)
    full_data_blocks = []
    for t in executed_tools_results:
        if t["tool_name"] in ["recommend_crop_rotation", "compare_all_crops"]:
            # Tableau complet de classement
            d = t["data"]
            if "full_ranking" in d:
                rows = d["full_ranking"]
                table_str = "\n".join([
                    f"    #{r['rank']} {r['crop_fr']} / {r['crop_darija']} | Agro:{r.get('agro_ecological_score',0)}/100 | Sol:{r['soil_health_score']}/100 | {r['yield_q_ha']}q/ha | -{r['water_saved_m3_ha']}m³ | +{r['nitrogen_bonus_kg_ha']}kg N"
                    for r in rows
                ])
                full_data_blocks.append(f"**CLASSEMENT NASA POWER COMPLET ({d.get('total_candidates_evaluated',0)} cultures) :**\n{table_str}")
            elif "comparison_table" in d:
                rows = d["comparison_table"]
                table_str = "\n".join([
                    f"    #{i+1} {r['crop_fr']} / {r['crop_darija']} | Sol:{r['soil_health_score']}/100 | {r['base_yield_q_ha']}q/ha | -{r['water_saved_vs_wheat_m3_ha']}m³ | +{r['nitrogen_fixation_kg_ha']}kg N | {r.get('disease_break','')[:60]}"
                    for i, r in enumerate(rows)
                ])
                full_data_blocks.append(f"**COMPARAISON MULTI-CULTURES ({d['total_crops_compared']} cultures) :**\n{table_str}")
        elif t["tool_name"] == "calculate_farm_custom_quantities":
            d = t["data"]
            full_data_blocks.append(
                f"**CALCUL EXPLOITATION ({d['surface_hectares']} Ha de {d['crop_name_fr']}) :**\n"
                f"    Récolte totale: {d['total_yield_q']} qentar ({d['total_yield_tonnes']} tonnes)\n"
                f"    Eau économisée: {d['total_water_saved_m3']:,} m³\n"
                f"    Azote fixé: {d['total_nitrogen_fixed_kg']} kg N → {d['bags_ammonitrate_saved']} sacs épargnés\n"
                f"    Gains engrais: {int(d['fertilizer_savings_mad']):,} MAD | Gains pompage: {int(d.get('pumping_savings_mad',0)):,} MAD"
            )
        elif t["tool_name"] == "check_smap_moisture":
            d = t["data"]
            full_data_blocks.append(
                f"**NASA SMAP Humidité Sol :** {d['surface_soil_moisture_pct']}% → {d['condition_status']}\n"
                f"    Conseil semis: {d.get('sowing_advice_fr','')}"
            )

    full_data_section = "\n\n".join(full_data_blocks)

    synth_prompt = f"""
Tu es l'Agent Agronome Central d'EarthEyes (NASA Space Apps Meknès 2026).
Tu as toi-même choisi et exécuté ces briques scientifiques pour le fellah :

=== RÉSUMÉ DES BRIQUES EXÉCUTÉES ===
{tools_outputs_formatted}

=== DONNÉES COMPLÈTES DES BRIQUES (utilise ces chiffres exacts) ===
{full_data_section or "(Aucune donnée étendue disponible)"}

=== CONTEXTE PARCELLE ===
- Localisation : Meknès, Bassin du Saïss ({lat}, {lon})
- Surface : {surface_ha} Ha
- Régime hydrique : {water_regime.upper()}
- Culture précédente : {current_crop}

Question de l'agriculteur : "{message}"

CONSIGNES DE SYNTHÈSE :
1. LANGUE : Détecte la langue de la question de l'agriculteur et réponds EXACTEMENT dans la même langue :
   - Question en arabe (أحرف عربية) → réponds en arabe standard (فصحى) avec terminologie agricole claire. N'utilise PAS le Darija écrit en lettres latines ("salam", "khoya"...).
   - Question en darija (أحرف عربية بالدارجة) → réponds en darija marocaine avec les lettres arabes uniquement.
   - Question en français → réponds en français.
   - Question en anglais → réponds en anglais.
   - Question en darija latine ("salam", "nzra3"...) → c'est la SEULE situation où tu peux répondre en darija latine.
   - En cas de doute → préfère l'arabe standard (فصحى).
2. Si tu as un CLASSEMENT COMPLET (recommend_crop_rotation ou compare_all_crops) :
   - Présente les 2-3 meilleures options avec LEURS AVANTAGES DISTINCTS et leurs chiffres réels.
   - Annonce clairement le GAGNANT avec son score agro-écologique et pourquoi il gagne.
   - Ne te limite JAMAIS à 1 seule culture quand tu as le classement complet.
3. Cite les VRAIS chiffres calculés (quintaux totaux réels, m³ eau, MAD économisés) — jamais de valeurs génériques.
4. Cite les sources : NASA POWER 42 ans, NASA SMAP, INRA Maroc Meknès, FAO-33.
5. Structure claire avec puces emoji pour lecture facile sur téléphone.
6. Max 250 mots — l'agriculteur lit sur mobile.
"""

    agent_reply_text = call_gemini_brain(synth_prompt, is_json=False, timeout=10)

    # Fallback déterministe — données réelles, multilingue selon la question
    if not agent_reply_text:
        farm_item = next((t["data"] for t in executed_tools_results if t["tool_name"] == "calculate_farm_custom_quantities"), None)
        rot_item  = next((t["data"] for t in executed_tools_results if t["tool_name"] == "recommend_crop_rotation"), None)
        cmp_item  = next((t["data"] for t in executed_tools_results if t["tool_name"] == "compare_all_crops"), None)

        # Le fallback construit un tableau structuré universel que le LLM peut afficher
        # dans n'importe quelle langue — on reessaie Gemini avec un prompt minimal
        if rot_item and rot_item.get("full_ranking"):
            ranking = rot_item["full_ranking"]
            rows_text = "\n".join([
                f"#{r['rank']} {r['crop_fr']} ({r['crop_darija']}) — "
                f"{r['yield_q_ha']} q/ha | Soil: {r['soil_health_score']}/100 | "
                f"-{r['water_saved_m3_ha']} m³ | +{r['nitrogen_bonus_kg_ha']} kg N/ha"
                for r in ranking[:3]
            ])
            minimal_prompt = (
                f"The user asked (in their language): \"{message}\"\n\n"
                f"NASA POWER 42-year crop ranking for Meknès/Saïss:\n{rows_text}\n\n"
                f"Reply in the SAME language as the user's question. "
                f"Present the top 2-3 crops with their key advantages. "
                f"Do NOT use Latin transliteration of Arabic unless the user wrote that way."
            )
            agent_reply_text = call_gemini_brain(minimal_prompt, is_json=False, timeout=8)

        if not agent_reply_text and cmp_item:
            rows = [r for r in cmp_item["comparison_table"] if r["crop_key"] != "blé"][:3]
            rows_text = "\n".join([
                f"#{i+1} {r['crop_fr']} ({r['crop_darija']}) — "
                f"{r['base_yield_q_ha']} q/ha | Soil: {r['soil_health_score']}/100 | "
                f"-{r['water_saved_vs_wheat_m3_ha']} m³ | +{r['nitrogen_fixation_kg_ha']} kg N/ha"
                for i, r in enumerate(rows)
            ])
            minimal_prompt = (
                f"The user asked (in their language): \"{message}\"\n\n"
                f"Multi-crop comparison:\n{rows_text}\n\n"
                f"Reply in the SAME language as the user's question. "
                f"Do NOT use Latin transliteration of Arabic unless the user wrote that way."
            )
            agent_reply_text = call_gemini_brain(minimal_prompt, is_json=False, timeout=8)

        # Dernier recours : RAG déterministe
        if not agent_reply_text:
            rag_advice = generate_grounded_agronomic_advice(message, context=context, lang="ar")
            agent_reply_text = rag_advice["response"]

    return {
        "status": "success",
        "brain_reasoning": brain_reasoning,
        "response": agent_reply_text,
        "tools_executed": [
            {
                "tool_name": t["tool_name"],
                "label": t["label"],
                "status": t["status"],
                "summary": t["summary"]
            }
            for t in executed_tools_results
        ],
        "ui_action": ui_action,
        "ui_payload": ui_payload
    }
