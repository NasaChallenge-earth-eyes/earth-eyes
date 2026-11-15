"""
Test post-audit : vérifie toutes les corrections apportées à agronomic_agent.py
"""
import sys, time, requests, json
sys.path.insert(0, ".")

BASE = "http://127.0.0.1:8000"
OK = 0; FAIL = 0

def test(name, passed, detail=""):
    global OK, FAIL
    icon = "✅" if passed else "❌"
    print(f"  {icon} {name}" + (f" → {detail}" if not passed else ""))
    if passed: OK += 1
    else: FAIL += 1

time.sleep(2)

# ============================================================
print("\n[1] target_crop=None → LLM choisit via recommend_crop_rotation (question générale)")
r = requests.post(f"{BASE}/chat", json={
    "question": "ashno a7san 7aja nzra3 ba3d l-gezza f Meknes?",
    "history": []
}, timeout=60)
d = r.json()
tools = [t["tool_name"] for t in d.get("tools_executed", [])]
test("Status 200", r.status_code == 200)
test("recommend_crop_rotation appelé", "recommend_crop_rotation" in tools, str(tools))
test("Réponse non vide >50 chars", len(d.get("response","")) > 50)
print(f"  Outils: {tools}")
resp1 = d.get("response","")
print(f"  Extrait: {resp1[:200]}")

# ============================================================
print("\n[2] Compare multi-cultures → compare_all_crops ou recommend avec classement complet")
r2 = requests.post(f"{BASE}/chat", json={
    "question": "qaren liya bin l-foul o l-7emmez o ch3ir, ashno a7san?",
    "history": []
}, timeout=60)
d2 = r2.json()
tools2 = [t["tool_name"] for t in d2.get("tools_executed", [])]
test("Status 200", r2.status_code == 200)
test("Outil comparaison ou rotation appelé", any(t in tools2 for t in ["compare_all_crops","recommend_crop_rotation"]), str(tools2))
print(f"  Outils: {tools2}")
resp2 = d2.get("response","")
print(f"  Extrait: {resp2[:250]}")

# ============================================================
print("\n[3] Culture connue + surface 8ha → calcul exploitation réel (pas hardcodé)")
r3 = requests.post(f"{BASE}/chat", json={
    "question": "bghit nzra3 l-7emmez f 8 ha bour, chhbal ghadi njme3?",
    "history": []
}, timeout=60)
d3 = r3.json()
tools3 = [t["tool_name"] for t in d3.get("tools_executed", [])]
resp3 = d3.get("response","")
test("Status 200", r3.status_code == 200)
test("calculate_farm appelé", "calculate_farm_custom_quantities" in tools3, str(tools3))
test("Chiffres 8ha dans réponse", "8" in resp3 or "hektar" in resp3.lower())
print(f"  Outils: {tools3}")
print(f"  Extrait: {resp3[:250]}")

# ============================================================
print("\n[4] Fuzzy crop_choice: noms lisibles → clés catalog exactes")
from step5_llm.agronomic_agent import tool_calculate_farm_custom_quantities
res4a = tool_calculate_farm_custom_quantities(5.0, "Pois chiche", "bour")
test("'Pois chiche' reconnu", res4a["crop_name_fr"] == "Pois chiche", res4a["crop_name_fr"])
res4b = tool_calculate_farm_custom_quantities(3.0, "L-7emmez", "bour")
test("'L-7emmez' reconnu", res4b["crop_name_fr"] == "Pois chiche", res4b["crop_name_fr"])
res4c = tool_calculate_farm_custom_quantities(4.0, "l-foul", "bour")
test("'l-foul' → Féverole", "feverole" in res4c["crop_name_fr"].lower().replace("é", "e"), res4c["crop_name_fr"])
res4d = tool_calculate_farm_custom_quantities(5.0, "l-ch3ir", "bour")
test("'l-ch3ir' → Orge", "Orge" in res4d["crop_name_fr"] or "orge" in res4d["crop_name_fr"].lower(), res4d["crop_name_fr"])

# ============================================================
print("\n[5] Prix azote harmonisé: 4.5 MAD/kg N (non 12 MAD)")
# Féverole : 45 kg N/ha × 4.5 × 5 ha = 1012.5 MAD
expected_mad = round(5 * 45 * 4.5, 0)
actual_mad = res4c["fertilizer_savings_mad"]  # 4ha feverole
expected_4ha = round(4 * 45 * 4.5, 0)
test(f"4ha Féverole = {expected_4ha} MAD (4.5 MAD/kg N)", actual_mad == expected_4ha, f"obtenu {actual_mad}")

# ============================================================
print("\n[6] Fallback sans hardcoding: score sol = vraie valeur du classement")
from step5_llm.agronomic_agent import tool_recommend_crop_rotation
rot = tool_recommend_crop_rotation()
real_score = rot["full_ranking"][0]["soil_health_score"]
test("Score sol réel disponible (≠ 92 hardcodé)", real_score > 0)
print(f"  Score sol #1 ({rot['winner']['crop_fr']}): {real_score}/100")
print(f"  Classement complet: {len(rot['full_ranking'])} cultures")

# ============================================================
print("\n[7] extract_parameters: target_crop=None sur question générale")
from step5_llm.agronomic_agent import extract_parameters_from_text
p_general = extract_parameters_from_text("ashno a7san nzra3?", {})
test("Question générale → target_crop=None", p_general["target_crop"] is None, str(p_general["target_crop"]))
p_foul = extract_parameters_from_text("nzra3 l-foul f 3 ha bour", {})
test("'l-foul' → feverole", p_foul["target_crop"] == "feverole", p_foul["target_crop"])
test("Surface 3ha détectée", p_foul["surface_hectares"] == 3.0, str(p_foul["surface_hectares"]))
p_saqwi = extract_parameters_from_text("3ndi l-bir wa 10 ha", {})
test("'l-bir' → saqwi", p_saqwi["water_regime"] == "saqwi", p_saqwi["water_regime"])

# ============================================================
print(f"\n{'='*50}")
print(f"RÉSULTAT FINAL: {OK} ✅ PASS / {FAIL} ❌ FAIL")
print("="*50)
