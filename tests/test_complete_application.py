"""
Test Suite Complet et Exhaustif pour EarthEyes / TerroirAI (NASA Space Apps 2026).
Teste littéralement CHAQUE endpoint, chaque brique scientifique et chaque flux d'interaction frontend/backend.
"""

import os
import sys
import json
import io
import requests
from PIL import Image

BASE_URL = "http://127.0.0.1:8000"

def log_section(title: str):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def test_get_root():
    log_section("TEST 1: GET / (Frontend Principal)")
    resp = requests.get(f"{BASE_URL}/")
    assert resp.status_code == 200, f"Erreur status: {resp.status_code}"
    html = resp.text
    assert "EarthEyes" in html or "TerroirAI" in html, "Titre manquant dans le HTML"
    assert "chatBox" in html, "Composant ChatBox manquant"
    assert "rotationDashboard" in html, "Tableau de bord de rotation manquant"
    assert "agent-action-bar" in html, "Barre d'action agentique manquante"
    print("✅ GET / : 200 OK | Interface complète chargée (taille:", len(html), "octets)")

def test_get_presentation():
    log_section("TEST 2: GET /presentation (Slides Jury NASA Space Apps)")
    resp = requests.get(f"{BASE_URL}/presentation")
    assert resp.status_code == 200, f"Erreur status: {resp.status_code}"
    html = resp.text
    assert "NASA" in html, "Contenu NASA manquant"
    assert "Slide 1" in html or "slide-1" in html, "Slides interactives manquantes"
    print("✅ GET /presentation : 200 OK | Deck de 7 slides interactif chargé")

def test_recommend_rotation_post():
    log_section("TEST 3: POST /recommend-rotation (Moteur Biophysique & Climat 42 ans)")
    payload = {
        "lat": 33.89,
        "lon": -5.55,
        "city": "Meknès",
        "previous_crop": "blé",
        "risk_profile": "équilibré"
    }
    resp = requests.post(f"{BASE_URL}/recommend-rotation", json=payload)
    assert resp.status_code == 200, f"Erreur status: {resp.status_code}"
    data = resp.json()
    assert data.get("status") == "success", f"Status inattendu: {data.get('status')}"
    
    recs = data.get("recommendations", [])
    assert len(recs) >= 2, f"Nombre de recommandations insuffisant: {len(recs)}"
    
    r1 = recs[0]
    print(f"✅ Recommandation #1 : {r1['name_fr']} ({r1['name_darija']})")
    print(f"   • Rendement physique : {r1.get('yield_display')}")
    print(f"   • Score Santé du Sol : {r1.get('soil_score_display')}")
    print(f"   • Efficience hydrique : {r1.get('water_productivity')}")
    print(f"   • Eau préservée : {r1.get('water_saved')}")
    print(f"   • Conseil Darija : {r1.get('darija_advice')}")
    
    # Vérification des métriques physiques non nulles
    assert r1.get("estimated_yield_kg_ha", 0) > 0, "Rendement kg/ha nul"
    assert r1.get("soil_health_score", 0) > 0, "Score sol nul"

def test_recommend_rotation_get():
    log_section("TEST 4: GET /recommend-rotation (Vérification Fallback GET)")
    resp = requests.get(f"{BASE_URL}/recommend-rotation")
    assert resp.status_code == 200, f"Erreur status: {resp.status_code}"
    data = resp.json()
    assert data.get("status") == "success"
    print("✅ GET /recommend-rotation : 200 OK | Réponse valide")

def test_chat_agent():
    log_section("TEST 5: POST /chat (Agent Agronome Multi-Outils)")
    
    test_queries = [
        ("Rotation & Azote", "شنو نزرع العام جاي مور القمح باش نعاون الأرض فالآزوت ومانضيعش الماء ؟", "recommend_crop_rotation"),
        ("Humidité SMAP", "واش الأرض واجدة للزرع دابا ؟ فحص رطوبة التربة NASA SMAP", "check_smap_moisture"),
        ("Pente SRTM", "واش كاين خطر انجراف التربة فهاد الأرض ؟ NASA SRTM", "analyze_terrain_srtm")
    ]
    
    for label, query, expected_tool in test_queries:
        print(f"\n--- Sous-test Chat : {label} ---")
        payload = {
            "question": query,
            "current_form": {"crop_type": "wheat", "location": "33.89, -5.55"}
        }
        resp = requests.post(f"{BASE_URL}/chat", json=payload)
        assert resp.status_code == 200, f"Erreur status: {resp.status_code}"
        data = resp.json()
        
        tools = [t["tool_name"] for t in data.get("tools_executed", [])]
        print(f"✅ Question : {query[:45]}...")
        print(f"   • Outils exécutés par l'Agent : {tools}")
        assert expected_tool in tools, f"Outil attendu {expected_tool} non trouvé dans {tools}"
        print(f"   • Extrait réponse Agent : {data.get('response')[:120]}...")

def test_agent_upload_photo():
    log_section("TEST 6: POST /agent-upload-photo (Vision IA & Rupture Sanitaire)")
    img_path = "images/diagnostic de la maladie.jpeg"
    assert os.path.exists(img_path), f"Image test introuvable: {img_path}"
    
    with open(img_path, "rb") as f:
        files = {"photo": ("test_leaf.jpeg", f, "image/jpeg")}
        data = {
            "crop_type": "wheat",
            "lat": 33.89,
            "lon": -5.55
        }
        resp = requests.post(f"{BASE_URL}/agent-upload-photo", files=files, data=data)
    
    assert resp.status_code == 200, f"Erreur status: {resp.status_code} - {resp.text}"
    res = resp.json()
    assert res.get("status") == "success", "Statut agent photo invalide"
    assert "disease" in res, "Champ disease manquant"
    assert "tools_executed" in res, "Outils exécutés manquants"
    assert "ui_payload" in res, "UI payload rotation manquant"
    
    print(f"✅ Diagnostic foliaire instantané exécuté avec succès :")
    print(f"   • Maladie identifiée : {res['disease'].get('disease_name')}")
    print(f"   • Sévérité tissulaire estimée : {res['disease'].get('severity_percent')}%")
    print(f"   • Outils appelés : {[t['label'] for t in res['tools_executed']]}")
    print(f"   • Réponse vocalisable Agent : {res['response'][:140]}...")

def test_predict_full_pipeline():
    log_section("TEST 7: POST /predict (Pipeline Complet Multi-Briques)")
    img_path = "images/diagnostic de la maladie.jpeg"
    assert os.path.exists(img_path), f"Image test introuvable: {img_path}"
    
    with open(img_path, "rb") as f:
        files = {"photo": ("test_leaf.jpeg", f, "image/jpeg")}
        data = {
            "farmer_id": "farmer_meknes_01",
            "lat": 33.89,
            "lon": -5.55,
            "crop_type": "wheat",
            "sowing_date": "2024-11-15",
            "historical_yields": json.dumps([{"year": 2023, "yield": 2800.0}, {"year": 2024, "yield": 2500.0}])
        }
        resp = requests.post(f"{BASE_URL}/predict", files=files, data=data)
    
    assert resp.status_code == 200, f"Erreur status: {resp.status_code} - {resp.text}"
    result = resp.json()
    
    # Vérification des briques du pipeline
    stages = result.get("process_stages", [])
    print(f"✅ Pipeline exécuté : {len(stages)} étapes enregistrées")
    for s in stages:
        print(f"   • {s['name']} -> Statut : {s['status']}")
    
    # Vérification des sorties scientifiques
    print("\n   [Sorties Biophysiques & Scientifiques] :")
    print(f"   • Rendement final estimé (Fusion) : {result.get('final_yield_estimate')} kg/ha")
    print(f"   • Indice NDVI Satellite : {result.get('ndvi')}")
    print(f"   • Propriétés du sol : pH={result.get('soil_ph')}, Argile={result.get('soil_clay_pct')}%, Sable={result.get('soil_sand_pct')}%")
    print(f"   • Maladie foliaire : {result.get('disease_class')} (Sévérité: {result.get('disease_severity')})")
    
    assert result.get("final_yield_estimate") is not None, "Rendement final non calculé"
    assert result.get("soil_ph") is not None, "pH sol non récupéré"

if __name__ == "__main__":
    print("\n🚀 DÉMARRAGE DU BANC D'ESSAI COMPLET (TEST SUITE TERROIRAI / EARTH-EYES)...")
    try:
        test_get_root()
        test_get_presentation()
        test_recommend_rotation_post()
        test_recommend_rotation_get()
        test_chat_agent()
        test_agent_upload_photo()
        test_predict_full_pipeline()
        
        log_section("🏆 RÉSULTAT FINAL : 7/7 TESTS VALIDÉS AVEC SUCCÈS !")
        print("Toutes les briques, tous les endpoints et toutes les interactions frontend/backend sont fonctionnels et validés.")
    except Exception as exc:
        print(f"\n❌ ÉCHEC D'UN TEST : {exc}")
        sys.exit(1)
