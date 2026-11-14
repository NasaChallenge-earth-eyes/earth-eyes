# TerroirAI: Climate-Resilient Crop Rotation for the Saïss Basin
## NASA International Space Apps Challenge 2026
**Challenge:** *Help Farmers Adapt to Climate Change*  
**Focus Area:** Saïss Agricultural Plain (Fès - Meknès, Morocco)  
**Authors:** Dev A (NASA Space Data & Simulation Engine) & Dev B (FastAPI Architecture, Farmer UI & Submission)  
**Language:** English (Official NASA Pitch Standard) | Duration: 3 Minutes (7 Slides)

---

## Slide 1: Title & Challenge Definition
- **Project Name:** **TerroirAI - Climate Rotation Advisor**
- **Tagline:** Empowering Moroccan smallholders to adapt crop rotations to accelerating drought using NASA Earth Observations.
- **Challenge Track:** *"Help Farmers Adapt to Climate Change"*
- **Geographic Focus:** The Saïss Plain (Meknès, Fès, El Hajeb), Morocco's agricultural granary facing unprecedented water stress.
- **Core Mission:** Shifting farmers from high-risk wheat monoculture to high-yield, water-saving resilient crop rotations supported by 40+ years of NASA satellite telemetry.

---

## Slide 2: The Climate Problem in the Saïss Plain
- **Drought Crisis:** Morocco has suffered 6 consecutive years of severe drought; major reservoirs operate below 25% capacity.
- **The Wheat Monoculture Trap:** Farmers traditionally re-sow soft and durum wheat season after season. Under current climatic shifts, late-spring heatwaves (*Chergui*) decimate grain filling, causing up to 60% harvest collapse.
- **Groundwater Depletion:** Saïss deep aquifers are falling by 1.5 to 2.0 meters annually due to emergency pumping.
- **The Farmer's Urgent Question:** *"What should I plant next season that will yield a profit with half the water?"*

---

## Slide 3: The NASA Earth Observation Data Pipeline
TerroirAI replaces generic forecasts with 4 decades of validated NASA Earth observations:
1. **NASA POWER (1984–2025):** 
   - 42-year continuous daily climate telemetry (precipitation, 2m temperature, solar radiation, reference ET0).
   - Proven Saïss trend: **+0.53°C temperature increase** and **-9.4% spring rainfall drop** during the critical grain maturation window.
2. **NASA SMAP (Soil Moisture Active Passive):**
   - High-resolution 9 km L3/L4 surface volumetric soil moisture (0–5 cm depth).
   - Validates sowing readiness in Saïss: benchmarked between **12% and 18%** volumetric water content to prevent false germination.
3. **NASA SRTM (Shuttle Radar Topography Mission 30m):**
   - Digital elevation and contour slope modeling to compute run-off velocity and erosion risk on Meknès undulating hillsides.
4. **MODIS & SoilGrids Integration:**
   - Multi-year NDVI phenology tracking merged with local soil physical properties (clay/sand/pH) to adjust Total Available Water (TAW).

---

## Slide 4: The Resilient Rotation & Soil Health Algorithm
Rather than an arbitrary financial black-box, TerroirAI ranks rotation candidates on biophysical harvest yields and long-term soil health:
- **Physical Harvest Yield (kg/ha & q/ha):** Multi-decadal empirical distribution (P10 dry year, P50 median, P90 optimal year). No price bias—grounded purely in crop biophysics.
- **Soil & Climate Resilience Index (/100):** Prioritizes biological nitrogen fixation (+35 to +45 kg N/ha), root structure, and disease cycle interruption.
- **Water Productivity (kg / m³ — FAO-33):** Physical yield produced per cubic meter of water (0.65 kg/m³ for chickpea vs 0.40 kg/m³ under wheat drought stress).
- **Water Stress Resilience (Win Rate):** % of historical drought seasons where the candidate crop retains a higher fraction of its yield potential than wheat.
- **Topographic Anti-Erosion Adaptability (NASA SRTM):** Deep taproots (sunflower, faba bean) preventing soil loss on slopes > 3%.
- **Agronomic RAG Assistant:** Bilingual chat grounded in verified publications from **INRA Maroc, FAO, and ICARDA**.

---

## Slide 5: Farmer-First Accessible User Experience
- **Zero Jargon:** No satellite coordinates or raw data tables. Farmers receive simple, high-impact recommendation cards.
- **Native Dual Language:** Full support for Moroccan Darija (spoken dialect) and French.
- **Single-Click Decision Support:** *"Chno nezre3 l-3am jay ? / Quoi planter après ?"* delivers immediate actionable rankings.
- **Culturally Tailored Agronomic Advice:**
  - *Chickpea:* "L-7emmez kay-sber l-jeffa o kay-3emmer l-ard b l-azot bla ma techri engrais."
  - *Early Barley:* "Ch3ir kay-wjed bekri qbel ma tji l-7arara dyal Chergui f chher 5."

---

## Slide 6: Validated Agro-Ecological & Physical Yield Impact
Simulated across 42 NASA POWER seasons (Meknès Saïss basin, 33.89°N, -5.55°W):
- **Recommendation #1 — Chickpea (L-7emmez, Legume):**
  - **Estimated Physical Yield:** **1,571 kg / ha** (15.7 q/ha) [P10: 998 — P90: 1,612 kg/ha]
  - **Soil Health Score:** **92 / 100** (+35 kg N/ha biological nitrogen fixed)
  - **Water Productivity (FAO-33):** **0.65 kg / m³** (consumes 43% less water than wheat)
  - **Water Saved:** **1,800 m³ / ha** conserved for groundwater recharge
  - **Sanitary Disruption:** Breaks wheat septoria & foot-rot disease cycles
- **Recommendation #2 — Faba Bean (L-Foul, Legume):**
  - **Estimated Physical Yield:** **2,061 kg / ha** (20.6 q/ha) [P10: 1,143 — P90: 2,126 kg/ha]
  - **Soil Health Score:** **95 / 100** (+45 kg N/ha biological nitrogen fixed)
  - **Soil Restructuring:** Powerful taproot decompacts dense clay soils (*Tirs*)
  - **Water Saved:** **1,000 m³ / ha** conserved
- **Recommendation #3 — Spring Sunflower (Nwwar Ch-Chems, Oilseed):**
  - **Estimated Physical Yield:** **1,381 kg / ha** (13.8 q/ha)
  - **Topographic Anti-Erosion:** 1.5m deep taproot anchoring slopes > 3% (NASA SRTM)

---

## Slide 7: Roadmap, Scientific Integrity & NASA Open Science
- **Strict Hackathon Integrity:** 100% open-source, non-commercial, documented NASA Open Data compliance.
- **Scalable Architecture:** Fast, lightweight FastAPI microservice designed to run on low-bandwidth rural mobile connections with intelligent local caching.
- **Expansion Horizons:** Extending calibration models from Saïss to Tadla, Haouz, and Chaouia agricultural perimeters.
- **Empowering Farmers Today:** Turning NASA space intelligence into livelihood security for Moroccan family farmers.
