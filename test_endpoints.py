import urllib.request
import json

def test_rotation():
    req = urllib.request.Request(
        'http://127.0.0.1:8000/recommend-rotation',
        data=json.dumps({'lat': 33.89, 'lon': -5.55, 'previous_crop': 'blé'}).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        print("=== RECOMMEND-ROTATION RESULT ===")
        print("City:", data.get("city"))
        print("Climate Alert:", data.get("climate_alert"))
        for r in data.get("recommendations", []):
            print(f"Rank #{r['rank']} {r['name_fr']} ({r['name_darija']})")
            print(f"   Rendement : {r.get('yield_display')}")
            print(f"   Plage P10-P90 : {r.get('yield_range')}")
            print(f"   Sol & Azote : {r.get('soil_score_display')} | {r.get('nitrogen_bonus')}")
            print(f"   Eau : {r.get('water_saved')} | {r.get('water_productivity')}")
            print(f"   Conseil Darija : {r.get('darija_advice')}")
            print("-" * 50)

def test_chat():
    req = urllib.request.Request(
        'http://127.0.0.1:8000/chat',
        data=json.dumps({
            'question': 'chno nzer3 mor l-qme7 bach n3awen l-ard b l-azot o ma n-kheserch l-ma ?',
            'current_form': {'crop_type': 'wheat'}
        }).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        print("=== CHAT RAG RESULT ===")
        print(data.get("response"))

if __name__ == "__main__":
    test_rotation()
    test_chat()
