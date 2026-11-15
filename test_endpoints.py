import urllib.request
import json
import requests

def test_photo_upload():
    print("=== TESTING AGENT PHOTO UPLOAD ===")
    url = "http://127.0.0.1:8000/agent-upload-photo"
    with open("images/diagnostic de la maladie.jpeg", "rb") as f:
        files = {"photo": ("leaf.jpeg", f, "image/jpeg")}
        data = {"crop_type": "wheat", "lat": 33.89, "lon": -5.55}
        resp = requests.post(url, files=files, data=data)
        print("Status code:", resp.status_code)
        res = resp.json()
        print("Disease detected:", res.get("disease", {}).get("disease_name"))
        print("Severity:", res.get("disease", {}).get("severity_percent"), "%")
        print("Tools executed:", [t["label"] for t in res.get("tools_executed", [])])
        print("Agent speech snippet:\n", res.get("response")[:300])

if __name__ == "__main__":
    test_photo_upload()
