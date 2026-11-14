# EarthEyes / TerroirAI: Climate-Adaptive Crop Rotation with NASA Earth Data
### NASA International Space Apps Challenge 2026 — Meknès Local & Global
**Challenge Track:** [Adapting Farms with NASA Data](https://www.spaceappschallenge.org/2026/challenges/adapting-farms-with-nasa-data/)  
**Territory Focus:** Saïss Plain (Meknès, Fès, El Hajeb), Morocco  
**Team EarthEyes:** Fatima Zahra Azzi & Samya (NASA Space Apps Challenge 2026)

---

## 🌍 Executive Summary
Morocco's Saïss plain is facing an unprecedented water crisis: 6 consecutive drought years, groundwater depletion exceeding 1.5 meters per year, and spring heatwaves (*Chergui*) causing harvest losses of up to 60% for traditional rainfed wheat.

**EarthEyes** empowers smallholder farmers to break the vulnerable wheat monoculture trap. Powered by **41 years of NASA POWER daily climate data (1984–2025)** and **NASA SMAP 9 km surface soil moisture telemetry**, EarthEyes calculates resilient crop rotations that maximize farmer net margins while drastically saving groundwater.

---

## 🛰️ NASA Space Data & Open Science Assets Used

| Dataset / Mission | Agency / Source | Spatial / Temporal Resolution | Purpose in EarthEyes |
| :--- | :--- | :--- | :--- |
| **NASA POWER** (Prediction Of Worldwide Energy Resources) | NASA Langley Research Center | 0.5° × 0.5° Daily (1984–2025) | 41-year agroclimatic baseline (daily precipitation, 2m temperature, solar radiation, ET0) proving the +1.2°C warming and -21.4% spring rainfall drop in Saïss. |
| **NASA SMAP** (Soil Moisture Active Passive) | NASA JPL / GSFC | 9 km (L3/L4 Surface 0–5 cm) | Real-time volumetric seedbed moisture at sowing time (calibrated to the 12%–18% Saïss optimum) to prevent false germination and adjust available soil water (TAW/RU). |
| **ESA Copernicus Sentinel-2 & MODIS** | ESA / NASA LP DAAC | 10 m / 250 m (Multi-temporal) | Historical vegetation vigor (NDVI) and phenological benchmarking. |
| **ISRIC SoilGrids v2.0** | ISRIC / Global Consortium | 250 m | Soil physical texture (clay, sand, organic carbon, pH) for available water holding capacity. |

---

## 🧠 Algorithmic Core: The 2-Era Climate Simulation Engine

EarthEyes compares crop performance across two climatic eras:
1. **Era 1 (Historical Baseline: 1984–2003)**
2. **Era 2 (Recent Climate Shift: 2004–2025)**

### Multi-Criteria Farmer Ranking Metrics:
1. **Win Rate vs Wheat (%):** Statistical frequency across 41 simulated seasons where an alternative crop beats conventional wheat profit.
2. **Water Productivity (MAD / m³):** Economic value generated per cubic meter of total water consumed (e.g. 3.92 MAD/m³ for chickpea vs < 1.50 MAD/m³ for rainfed wheat).
3. **Biological Nitrogen Fixation Bonus:** Legumes fix up to +35 kg N/ha, eliminating synthetic fertilizer expenditures.
4. **Phytosanitary & Weed Disruption:** Breaking root pathogen cycles (*Fusarium*, *Septoria*) detected by the leaf diagnostics module.

---

## 📱 Farmer-Centric Bilingual Interface (Darija & French)

Smallholders access instant decision support without technical jargon:
- **One-Click Action:** *"Quoi planter après ? / شنو نزرع العام جاي ؟"*
- **Bilingual Guidance:** Interactive UI in Moroccan Darija and French.
- **Actionable Advice:**
  - *Chickpea (L-7emmez):* *"L-7emmez kay-sber l-jeffa o kay-3emmer l-ard b l-azot bla engrais."*
  - *Early Barley (Ch3ir):* *"Ch3ir kay-wjed bekri qbel ma tji l-7arara dyal Chergui f chher 5."*

---

## 🛠️ Architecture & Quickstart

```bash
# Clone the repository
git clone https://github.com/NasaChallenge-earth-eyes/earth-eyes.git
cd earth-eyes

# Create & activate environment
conda create -n eartheyes python=3.12 -y
conda activate eartheyes

# Install requirements
pip install -r requirements.txt

# Run FastAPI server
python app.py
# Or: uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

- **Interactive Farmer App:** `http://127.0.0.1:8000/`
- **NASA Space Apps Pitch (7 Slides):** `http://127.0.0.1:8000/presentation`
- **FastAPI OpenAPI Docs:** `http://127.0.0.1:8000/docs`
- **Rotation Recommendation API:** `POST /recommend-rotation`

---

## ⚖️ Hackathon Integrity & AI Disclosure
In strict adherence to NASA Space Apps Challenge 2026 rules:
- Pre-existing components (academic leaf disease models) are clearly distinguished in [HACKATHON_SCOPE.md](HACKATHON_SCOPE.md).
- All NASA POWER ingestion pipelines, 2-era climate simulations, water productivity modules, and bilingual farmer UI were created 100% during the hackathon period (Nov 14–15, 2026).
