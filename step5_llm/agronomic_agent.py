"""
Agent Agronome Autonome Multi-Outils (EarthEyes / TerroirAI - NASA Space Apps 2026).
Orchestre les briques scientifiques et géophysiques :
1. NASA POWER (1984-2025) & Moteur de Rotation Résiliente (Step 7)
2. NASA SMAP Humidité de surface du sol 0-5cm (Step 2)
3. NASA SRTM 30m Topographie, altitude et anti-érosion (Step 7)
4. RAG Agronomique INRA Maroc / FAO-33 / ICARDA (Step 5)
5. Simulation Biophysique WOFOST (Step 4)
6. Diagnostic Foliar CNN (Step 1)
"""

import os
import json
import re
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Charger les variables d'environnement (.env)
load_dotenv()

try:
    import google.generativeai as genai
except ImportError:
    genai = None

# Imports des briques scientifiques du projet
from step7_rotation.rotation_engine import recommend_crop_rotation
from step2_soil.smap_soil import get_smap_moisture
from step7_rotation.terrain_slope import get_srtm_terrain_profile
from step5_llm.rag_agronomy import (
    retrieve_agronomic_knowledge,
    format_rag_context_for_prompt,
    generate_grounded_agronomic_advice
)

# Configuration de Gemini
api_key = os.environ.get("GEMINI_API_KEY", "")
if api_key and genai is not None:
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        print(f"[Agent] Avertissement configuration genai: {e}")

MODEL_NAME = "models/gemini-2.5-flash"

# Définition des métadonnées des outils
AGENT_TOOLS_METADATA = [
    {
        "name": "recommend_crop_rotation",
        "label": "🌾 NASA POWER 42 ans & Rotation Résiliente",
        "description": "Simule 42 saisons historiques (1984-2025) et recommande les meilleures cultures en kg/ha, santé du sol et économie d'eau après la culture actuelle.",
        "parameters": ["lat", "lon", "previous_crop", "risk_profile"]
    },
    {
        "name": "check_smap_moisture",
        "label": "🛰️ NASA SMAP Humidité au Semis (0-5cm)",
        "description": "Mesure l'humidité volumétrique réelle de surface (calibrée 12-18% Saïss) pour valider si le sol est prêt pour le semis.",
        "parameters": ["lat", "lon"]
    },
    {
        "name": "analyze_terrain_srtm",
        "label": "⛰️ NASA SRTM 30m Topographie & Anti-Érosion",
        "description": "Évalue l'altitude et le pourcentage de pente de la parcelle pour prévenir l'érosion hydrique et conseiller le labour en courbes de niveau.",
        "parameters": ["lat", "lon"]
    },
    {
        "name": "consult_rag_knowledge",
        "label": "📚 RAG Agronomique INRA Maroc / FAO / ICARDA",
        "description": "Consulte les bulletins scientifiques officiels sur la fixation d'azote, la rupture parasitaire et l'efficience de l'eau.",
        "parameters": ["query", "crop"]
    }
]

def execute_tool(tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Exécuteur universel des outils scientifiques du projet.
    """
    lat = float(args.get("lat") or 33.89)
    lon = float(args.get("lon") or -5.55)

    if tool_name == "recommend_crop_rotation":
        prev = args.get("previous_crop") or "blé"
        risk = args.get("risk_profile") or "équilibré"
        res = recommend_crop_rotation(lat=lat, lon=lon, previous_crop=prev, risk_profile=risk)
        return {
            "tool": tool_name,
            "label": "🌾 NASA POWER 42 ans & Rotation Résiliente",
            "status": "success",
            "ui_action": "SHOW_ROTATION",
            "data": res,
            "summary": f"Calculé sur 42 saisons : #1 {res['recommendations'][0]['crop_name_fr']} ({res['recommendations'][0]['estimated_yield_kg_ha']} kg/ha, Sol: {res['recommendations'][0]['soil_health_score']}/100)"
        }

    elif tool_name == "check_smap_moisture":
        smap_data = get_smap_moisture(lat=lat, lon=lon)
        return {
            "tool": tool_name,
            "label": "🛰️ NASA SMAP Humidité au Semis",
            "status": "success",
            "ui_action": "SHOW_SOIL",
            "data": smap_data,
            "summary": f"Humidité SMAP {smap_data.get('surface_soil_moisture_m3_m3', 0.14)*100:.1f}% ({smap_data.get('sowing_readiness', 'Optimal')})"
        }

    elif tool_name == "analyze_terrain_srtm":
        terrain = get_srtm_terrain_profile(lat=lat, lon=lon)
        return {
            "tool": tool_name,
            "label": "⛰️ NASA SRTM 30m Topographie & Anti-Érosion",
            "status": "success",
            "ui_action": "SHOW_TERRAIN",
            "data": terrain,
            "summary": f"Altitude {terrain['elevation_m']}m, Pente {terrain['slope_percent']}% ({terrain['erosion_risk_fr']})"
        }

    elif tool_name == "consult_rag_knowledge":
        q = args.get("query") or "rotation blé Saïss"
        c = args.get("crop") or "blé"
        chunks = retrieve_agronomic_knowledge(q, target_crop=c, top_k=2)
        return {
            "tool": tool_name,
            "label": "📚 RAG INRA Maroc / FAO",
            "status": "success",
            "ui_action": "SHOW_RAG",
            "data": chunks,
            "summary": f"Extrait {len(chunks)} références : {chunks[0]['title']}"
        }

    return {"tool": tool_name, "status": "error", "summary": "Outil inconnu"}


def run_agronomic_agent(
    message: str,
    history: Optional[List[Dict[str, Any]]] = None,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Point d'entrée de l'Agent Agronome Autonome.
    Analyse le message, sélectionne et exécute les outils appropriés,
    et formule une réponse pédagogique en Darija et en Français.
    """
    context = context or {}
    history = history or []
    lat = float(context.get("lat") or 33.89)
    lon = float(context.get("lon") or -5.55)
    current_crop = context.get("crop_type") or "blé"

    clean_msg = message.lower()
    tools_to_run = []

    # 1. Détection intelligente de l'intention et des outils nécessaires
    # A) Rotation / Quoi planter après
    if any(k in clean_msg for k in ["rotation", "planter", "زرع", "شنو نزرع", "بعد", "mor", "apres", "après", "l-3am jay", "choix", "alternative"]):
        tools_to_run.append(("recommend_crop_rotation", {"lat": lat, "lon": lon, "previous_crop": current_crop}))
        tools_to_run.append(("consult_rag_knowledge", {"query": clean_msg, "crop": current_crop}))

    # B) Humidité / SMAP / Semis / Chta
    if any(k in clean_msg for k in ["humidité", "humidite", "smap", "semis", "bder", "زرع", "chta", "pluie", "sol prêt", "moisture"]):
        tools_to_run.append(("check_smap_moisture", {"lat": lat, "lon": lon}))

    # C) Pente / Érosion / SRTM / Terrain
    if any(k in clean_msg for k in ["pente", "hadra", "érosion", "erosion", "srtm", "terrain", "coteau", "ravinement"]):
        tools_to_run.append(("analyze_terrain_srtm", {"lat": lat, "lon": lon}))

    # Par défaut, si question ouverte, au moins RAG
    if not tools_to_run:
        tools_to_run.append(("consult_rag_knowledge", {"query": clean_msg, "crop": current_crop}))

    # 2. Exécution effective des outils
    executed_tools_results = []
    ui_action = None
    ui_payload = None

    for t_name, t_args in tools_to_run:
        try:
            res = execute_tool(t_name, t_args)
            executed_tools_results.append(res)
            # Prioriser l'UI action majeure (Rotation en priorité)
            if res.get("ui_action") == "SHOW_ROTATION" or ui_action is None:
                ui_action = res.get("ui_action")
                ui_payload = res.get("data")
        except Exception as e:
            print(f"[Agent Tool Execution Error] {t_name}: {e}")

    # 3. Synthèse des résultats d'outils pour l'explication finale
    tool_summaries_text = "\n".join([f"- Outil {t['label']} : {t['summary']}" for t in executed_tools_results])
    
    # Extraits RAG éventuels
    rag_extracts = ""
    rag_tool_res = next((t for t in executed_tools_results if t["tool"] == "consult_rag_knowledge"), None)
    if rag_tool_res and rag_tool_res.get("data"):
        rag_extracts = format_rag_context_for_prompt(rag_tool_res["data"])

    # 4. Génération de la réponse via Gemini (si configuré) ou Fallback expert
    agent_reply_text = ""
    if os.environ.get("GEMINI_API_KEY") and genai is not None:
        try:
            model = genai.GenerativeModel(MODEL_NAME)
            prompt = f"""
            Tu es l'Agent Agronome Central d'EarthEyes (NASA Space Apps 2026).
            Tu es un expert agronome de terrain au Maroc (région Saïss / Meknès).
            Tu viens d'exécuter des outils scientifiques pour répondre à l'agriculteur.

            === RÉSULTATS DES OUTILS EXÉCUTÉS ===
            {tool_summaries_text}

            === CONNAISSANCES RAG SOURCÉES (INRA / FAO / ICARDA) ===
            {rag_extracts}

            === CONTEXTE PARCELLE ===
            - Localisation : Meknès ({lat}, {lon})
            - Culture actuelle/précédente : {current_crop}

            Question de l'agriculteur : "{message}"

            CONSIGNES :
            1. Réponds en Darija marocaine claire et bienveillante (avec traduction/termes français si utile).
            2. Fais référence explicite aux résultats d'outils (ex: les kg/ha simulés sur 42 ans de données NASA, le score de santé du sol, l'humidité SMAP).
            3. Cite toujours l'autorité scientifique (INRA Maroc, FAO-33).
            4. Reste concret et encourageant.
            """
            response = model.generate_content(prompt)
            agent_reply_text = response.text.strip()
        except Exception as e:
            print(f"[Agent Gemini Call Failed] {e}")

    # Fallback déterministe si Gemini n'a pas répondu
    if not agent_reply_text:
        # Si la rotation a été exécutée
        rot_tool = next((t for t in executed_tools_results if t["tool"] == "recommend_crop_rotation"), None)
        if rot_tool:
            best = rot_tool["data"]["recommendations"][0]
            sec = rot_tool["data"]["recommendations"][1]
            agent_reply_text = (
                f"🌱 **Nasi7a dyal l-Agent EarthEyes (NASA POWER 42 ans) :**\n\n"
                f"Mor l-gezza (l-qme7), a7sen 7aja l-ard dyalek f Meknès hiya t-qleb b **{best['crop_name_darija']} ({best['crop_name_fr']})** !\n"
                f"• **Ghella l-motawaqqi3a :** {best['estimated_yield_kg_ha']} kg/ha ({best['estimated_yield_q_ha']} q/ha)\n"
                f"• **Se77at trab (Score Sol) :** {best['soil_health_score']}/100 (+{best['nitrogen_bonus_kg_ha']} kg N/ha dyal l-azot naturel)\n"
                f"• **L-ma li ghadi twaffer :** {best['water_saved_m3_ha']} m³/ha\n\n"
                f"Ila bghiti khtar tani : **{sec['crop_name_darija']} ({sec['crop_name_fr']})** kat-3ti {sec['estimated_yield_kg_ha']} kg/ha o kat-7el trab l-ghliya.\n\n"
                f"📚 *Al-Marji3 :* INRA Maroc Meknès & Directive FAO-33."
            )
        else:
            rag_advice = generate_grounded_agronomic_advice(message, context=context, lang="ar")
            agent_reply_text = rag_advice["response"]

    return {
        "status": "success",
        "response": agent_reply_text,
        "tools_executed": [
            {
                "tool_name": t["tool"],
                "label": t["label"],
                "status": t["status"],
                "summary": t["summary"]
            }
            for t in executed_tools_results
        ],
        "ui_action": ui_action,
        "ui_payload": ui_payload
    }
