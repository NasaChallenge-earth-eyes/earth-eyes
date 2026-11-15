"""
Test suite validating LLM Brain flexibility, dynamic argument injection,
the 11 scientific tools, and unconstrained decision logic.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from step5_llm.agronomic_agent import (
    ALL_TOOLS_CALLABLE,
    tool_recommend_crop_rotation,
    tool_compare_all_crops,
    tool_calculate_farm_custom_quantities,
    tool_check_smap_moisture,
    tool_analyze_terrain_srtm,
    tool_get_soil_physicochemistry,
    tool_check_satellite_ndvi,
    tool_analyze_nasa_climate_trend,
    tool_predict_crop_yield_ai,
    tool_diagnose_crop_pathology,
    tool_consult_rag_knowledge,
    diagnose_leaf_with_vision,
    run_agronomic_agent
)
from step5_llm.rag_agronomy import retrieve_agronomic_knowledge, generate_grounded_agronomic_advice
from PIL import Image

def test_11_tools_registered():
    print("[TEST 1] Vérification des 11 briques scientifiques enregistrées...")
    expected_tools = [
        "recommend_crop_rotation",
        "check_smap_moisture",
        "analyze_terrain_srtm",
        "get_soil_physicochemistry",
        "check_satellite_ndvi",
        "calculate_farm_custom_quantities",
        "compare_all_crops",
        "analyze_nasa_climate_trend",
        "predict_crop_yield_ai",
        "diagnose_crop_pathology",
        "consult_rag_knowledge"
    ]
    for t in expected_tools:
        assert t in ALL_TOOLS_CALLABLE, f"Outil manquant : {t}"
    print("  -> Les 11 briques scientifiques sont bien enregistrées dans ALL_TOOLS_CALLABLE.")

def test_tool_executions():
    print("[TEST 2] Exécution directe des 3 nouvelles briques...")
    
    # 1. Tendance climatique NASA
    clim = tool_analyze_nasa_climate_trend(33.89, -5.55)
    assert clim["status"] == "success"
    assert "temperature_warming" in clim
    assert "spring_rainfall_shift" in clim
    print(f"  -> Climat NASA : {clim['temperature_warming']}, pluie {clim['spring_rainfall_shift']}")

    # 2. Prédiction IA Rendement
    yield_ai = tool_predict_crop_yield_ai(crop="feverole", surface_hectares=10.0, water_regime="bour")
    assert yield_ai["status"] == "success"
    assert yield_ai["estimated_yield_q_ha"] > 0
    assert yield_ai["total_harvest_q"] > 0
    print(f"  -> Rendement IA Féverole : {yield_ai['estimated_yield_q_ha']} q/ha, Total {yield_ai['total_harvest_q']} Qtx")

    # 3. Pathologie et rupture sanitaire
    patho = tool_diagnose_crop_pathology(crop_type="blé", symptoms_or_disease="jaunissement et pourriture du collet")
    assert patho["status"] == "success"
    assert "sanitary_break_solution" in patho
    print(f"  -> Pathologie Blé : Rupture conseillée -> {patho['sanitary_break_solution']}")

def test_dynamic_argument_forwarding():
    print("[TEST 3] Vérification de l'injection dynamique des arguments décidés par le LLM...")
    # On simule un appel où le LLM a choisi 8 hectares et féverole (non par défaut)
    agent_res = run_agronomic_agent(
        message="Combien de quintaux et quel gain d'engrais sur 8 hectares de féverole ?",
        context={"surface_hectares": 8, "crop_type": "feverole", "water_regime": "bour"}
    )
    assert agent_res["status"] == "success"
    executed = agent_res["tools_executed"]
    assert len(executed) > 0
    print(f"  -> Outils exécutés ({len(executed)}) : {[t['tool_name'] for t in executed]}")

def test_arabic_rag_and_leaf_vision():
    print("[TEST 4] Vérification RAG arabe standard et vision foliaire...")
    # RAG en arabe standard
    chunks = retrieve_agronomic_knowledge("دورة زراعية حمص أزوت")
    assert len(chunks) > 0
    assert "content_ar" in chunks[0]
    assert len(chunks[0]["content_ar"]) > 50
    print(f"  -> RAG Arabe : extrait {chunks[0]['content_ar'][:80]}...")

    # Vision foliaire CNN
    dummy_img = Image.new("RGB", (224, 224), color=(34, 139, 34))
    diag = diagnose_leaf_with_vision(dummy_img, crop_type="wheat")
    assert "disease_name" in diag
    assert "severity_percent" in diag
    print(f"  -> Vision CNN : {diag['disease_name']}, sévérité: {diag['severity_percent']}%")

if __name__ == "__main__":
    test_11_tools_registered()
    test_tool_executions()
    test_dynamic_argument_forwarding()
    test_arabic_rag_and_leaf_vision()
    print("\n✅ TOUS LES TESTS DE FLEXIBILITÉ ET BRIQUES SCIENTIFIQUES PASSENT AVEC SUCCÈS !")
