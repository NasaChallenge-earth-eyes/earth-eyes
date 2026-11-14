"""
Moteur de décision agronomique et agro-écologique de rotation des cultures (NASA Space Apps 2026).
Simule 42 saisons agricoles réelles (1984-2025) via NASA POWER pour le Saïss (Meknès).
Évalue le rendement physique attendu (kg/ha et quintaux/ha), la résilience hydrique (Win Rate),
la régénération de la santé du sol (fixation d'azote biologique) et l'anti-érosion topographique (NASA SRTM 30m).
Basé sur les référentiels INRA Maroc, FAO-33, FAO-56 et ICARDA.
"""

import numpy as np
from typing import Dict, Any, List, Optional

from .nasa_climate_client import NASAClimateClient
from .crop_catalog import CROP_CATALOG
from .water_productivity import (
    calculate_water_productivity_kg_m3,
    calculate_water_saved_vs_baseline,
    calculate_nitrogen_monetary_bonus
)
from .terrain_slope import get_srtm_terrain_profile

def recommend_crop_rotation(
    lat: float = 33.89,
    lon: float = -5.55,
    previous_crop: str = "blé",
    risk_profile: str = "équilibré",
    detected_disease: str = "none",
    slope_pct: Optional[float] = None
) -> Dict[str, Any]:
    """
    Fonction principale de recommandation de rotation culturale sous stress climatique.
    Intègre les données physiques NASA POWER (1984-2025) et la topographie NASA SRTM 30m.
    Fournit des prédictions physiques en kg/ha (sans biais de prix artificiel)
    et priorise la santé durable des sols du bassin de Meknès.
    """
    client = NASAClimateClient(lat, lon)
    climate_analysis = client.analyze_two_eras()

    # Analyse topographique NASA SRTM (Élévation et pente de la parcelle)
    terrain_profile = get_srtm_terrain_profile(lat, lon, user_slope_pct=slope_pct)
    actual_slope = terrain_profile["slope_percent"]

    # Extraction des séries pluviométriques de printemps par année (Mars-Mai)
    params = client.data.get("properties", {}).get("parameter", {})
    rain_dict = params.get("PRECTOTCORR", {})

    spring_rains_by_year = {}
    years = sorted(list(set(k[:4] for k in rain_dict.keys())))
    for y_str in years:
        spring_vals = [
            v for k, v in rain_dict.items()
            if (k.startswith(f"{y_str}03") or k.startswith(f"{y_str}04") or k.startswith(f"{y_str}05")) and v != -999.0
        ]
        if spring_vals:
            spring_rains_by_year[y_str] = sum(spring_vals)

    # Référence normale de pluie printanière (médiane sur la série 1984-2025)
    all_spring_rains = list(spring_rains_by_year.values())
    normal_spring_rain = float(np.median(all_spring_rains)) if all_spring_rains else 165.0

    # Simulation année par année du taux de rétention de potentiel pour le blé (référence)
    wheat_info = CROP_CATALOG["blé"]
    wheat_retention_by_year = {}
    wheat_yield_by_year = {}
    for y_str, rain in spring_rains_by_year.items():
        water_stress = max(0.0, 1.0 - (rain / normal_spring_rain))
        retention = max(0.20, 1.0 - (wheat_info["drought_sensitivity"] * water_stress))
        wheat_retention_by_year[y_str] = retention
        wheat_yield_by_year[y_str] = wheat_info["base_yield_kg_ha"] * retention

    # Évaluation agro-écologique et biophysique de chaque culture candidate
    candidates_results = []
    prev_crop_clean = previous_crop.lower().strip()

    for crop_id, crop in CROP_CATALOG.items():
        # Règle agronomique stricte anti-monoculture : pas de reconduction de la même culture
        if crop_id == prev_crop_clean or (crop_id == "blé" and "blé" in prev_crop_clean):
            continue

        yields_all_years = []
        resilience_wins_vs_wheat = 0
        total_recent_years = 0

        # Facteur d'adaptation topographique NASA SRTM :
        # Sur sol en pente (>= 3%), les racines pivotantes profondes évitent le ravinement
        erosion_prot = crop.get("erosion_protection_score", 1.0)
        slope_adjustment = 1.0
        if actual_slope >= 3.0:
            slope_adjustment = 1.0 + (actual_slope / 100.0) * (erosion_prot - 1.0)

        # Vérification rupture sanitaire face aux maladies transmises par le sol
        has_disease_penalty = False
        if "septoria" in detected_disease.lower() and crop["family"] == "céréale":
            has_disease_penalty = True

        for y_str, rain in spring_rains_by_year.items():
            water_stress = max(0.0, 1.0 - (rain / normal_spring_rain))
            retention_fraction = max(0.25, 1.0 - (crop["drought_sensitivity"] * water_stress))

            # Rendement physique simulé en kg/ha
            realized_yield = crop["base_yield_kg_ha"] * retention_fraction * slope_adjustment

            # Malus sanitaire si même famille qu'un pathogène terricole déclaré
            if has_disease_penalty:
                realized_yield *= 0.72  # Rupture non assurée : -28% de rendement

            yields_all_years.append(realized_yield)

            # Win Rate climatique (2004-2025) :
            # La culture gagne si sa conservation de potentiel sous sécheresse bat celle du blé
            y = int(y_str)
            if y >= 2004:
                total_recent_years += 1
                if retention_fraction > wheat_retention_by_year.get(y_str, 0.0):
                    resilience_wins_vs_wheat += 1

        win_rate = round((resilience_wins_vs_wheat / total_recent_years) * 100) if total_recent_years > 0 else 70

        # Distribution physique des rendements (kg/ha)
        p10_kg = float(np.percentile(yields_all_years, 10))
        p50_kg = float(np.percentile(yields_all_years, 50))
        p90_kg = float(np.percentile(yields_all_years, 90))

        # Efficience physique de l'eau (FAO-33) : kg récolté par m³ d'eau consommé
        water_prod_kg_m3 = calculate_water_productivity_kg_m3(p50_kg, crop["water_need_m3_ha"])
        water_saved_m3 = calculate_water_saved_vs_baseline(crop["water_need_m3_ha"], wheat_info["water_need_m3_ha"])

        # Score Agro-Écologique Global (/100) :
        # - Santé du sol & Azote biologique : 40%
        # - Résilience sécheresse & Économie d'eau : 35%
        # - Rupture sanitaire des maladies : 15%
        # - Protection topographique anti-érosion : 10%
        s_soil = crop["soil_health_score"]
        s_water = min(100.0, (win_rate * 0.6) + ((water_saved_m3 / 2500.0) * 40.0))
        s_sanitary = 40.0 if has_disease_penalty else 100.0
        s_slope = min(100.0, erosion_prot * 75.0)

        agro_score = (0.40 * s_soil) + (0.35 * s_water) + (0.15 * s_sanitary) + (0.10 * s_slope)

        candidates_results.append({
            "crop_id": crop_id,
            "crop_name_fr": crop["name_fr"],
            "crop_name_darija": crop["name_darija"],
            "family": crop["family"].capitalize(),
            # Rendement physique en kg/ha et quintaux/ha (1 q = 100 kg)
            "estimated_yield_kg_ha": round(p50_kg),
            "estimated_yield_q_ha": round(p50_kg / 100.0, 1),
            "yield_p10_kg_ha": round(p10_kg),
            "yield_p50_kg_ha": round(p50_kg),
            "yield_p90_kg_ha": round(p90_kg),
            "yield_p10_q_ha": round(p10_kg / 100.0, 1),
            "yield_p50_q_ha": round(p50_kg / 100.0, 1),
            "yield_p90_q_ha": round(p90_kg / 100.0, 1),
            # Indicateurs agro-écologiques et régénératifs
            "soil_health_score": crop["soil_health_score"],
            "agro_ecological_score": round(agro_score, 1),
            "nitrogen_bonus_kg_ha": int(crop["nitrogen_fixation_kg_ha"]),
            "water_saved_m3_ha": int(water_saved_m3),
            "water_productivity_kg_m3": water_prod_kg_m3,
            "win_rate_vs_wheat_percent": win_rate,
            "root_type": crop.get("root_type", "moyen"),
            "soil_health_impact": crop["soil_health_fr"],
            "darija_summary": crop["soil_health_darija"],
            # Compatibilité UI existante
            "margin_mad_ha": round(p50_kg)  # Affiche le rendement kg/ha comme valeur principale
        })

    # Classement raisonné selon le profil agronomique souhaité
    risk = risk_profile.lower().strip()
    if risk == "prudent":
        # Sécurité minimale de récolte en année sèche (P10) + Santé du sol
        candidates_results.sort(key=lambda x: (x["yield_p10_kg_ha"] * 0.4 + x["agro_ecological_score"] * 20), reverse=True)
    elif risk == "ambitieux":
        # Rendement maximum en bonne année (P90) + Santé du sol
        candidates_results.sort(key=lambda x: (x["yield_p90_kg_ha"] * 0.4 + x["agro_ecological_score"] * 20), reverse=True)
    else:  # équilibré (défaut) : trie sur le Score Agro-Écologique Global
        candidates_results.sort(key=lambda x: x["agro_ecological_score"], reverse=True)

    # Attribution des rangs d'excellence agronomique (1, 2, 3...)
    for idx, c in enumerate(candidates_results):
        c["rank"] = idx + 1

    return {
        "status": "success",
        "location": {
            "city": "Meknès",
            "lat": lat,
            "lon": lon
        },
        "climate_trend_nasa": {
            "baseline_period": climate_analysis["era1_period"],
            "recent_period": climate_analysis["era2_period"],
            "temp_increase_celsius": climate_analysis["temp_increase_celsius"],
            "spring_rain_decrease_percent": climate_analysis["spring_rain_decrease_percent"]
        },
        "terrain_srtm": {
            "elevation_m": terrain_profile["elevation_m"],
            "slope_percent": terrain_profile["slope_percent"],
            "erosion_risk": terrain_profile["erosion_risk_fr"],
            "anti_erosion_advice_fr": terrain_profile["anti_erosion_advice_fr"],
            "anti_erosion_advice_darija": terrain_profile["anti_erosion_advice_darija"]
        },
        "previous_crop": previous_crop,
        "risk_profile": risk_profile,
        "recommendations": candidates_results[:3],
        "disclaimer": "Les rendements estimés (kg/ha) sont issus de simulations biophysiques calées sur 42 années de données NASA POWER et ne constituent pas une garantie contractuelle."
    }
