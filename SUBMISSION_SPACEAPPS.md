# 📝 NASA Space Apps Challenge 2026 — Official Submission Document
**Project Title:** EarthEyes: Climate-Adaptive Crop Rotation with NASA Earth Data  
**Challenge:** [Adapting Farms with NASA Data](https://www.spaceappschallenge.org/2026/challenges/adapting-farms-with-nasa-data/)  
**Location:** Meknès Local Event & Global Judging  
**Repository:** https://github.com/NasaChallenge-earth-eyes/earth-eyes  

---

## 1. Short Project Description (Elevator Pitch)
*Limit: 250 characters*

> EarthEyes leverages 41 years of NASA POWER climate data and NASA SMAP soil moisture to help Moroccan smallholder farmers break vulnerable wheat monoculture, boosting farm margins by +32% while saving 1,800 m³/ha of groundwater.

---

## 2. Detailed Project Summary
*Limit: 1,500 words*

### The Challenge
In the agricultural basin of the Saïss plain (Meknès, Morocco), smallholder family farmers face a devastating reality: six consecutive years of drought, groundwater depletion exceeding 1.5 meters per year, and frequent springtime heatwaves (*Chergui*) that cause up to 60% harvest collapse in traditional rainfed wheat monocultures. Farmers are caught in a vicious cycle: re-sowing wheat out of habit, suffering crop failure, taking on debt, and dangerously over-pumping deep aquifers.

### The EarthEyes Solution
EarthEyes is an open-source, farmer-first decision support system that transforms 41 years of NASA Earth Observations into immediate, actionable crop rotation recommendations. 

Instead of treating weather as an unpredictable mystery, EarthEyes analyzes historical climate shift between two distinct 21-year eras (1984–2003 vs. 2004–2025) using the **NASA POWER API**. It demonstrates a localized **+1.2°C temperature anomaly** and a **-21.4% collapse in spring rainfall** during the critical grain filling window. 

Complementing long-term climate shift, **NASA SMAP (Soil Moisture Active Passive)** provides 9 km surface volumetric seedbed moisture (0–5 cm depth), verifying whether seasonal sowing moisture falls within the proven 12%–18% germination window in the Saïss plain.

### Key Innovations & Algorithmic Scoring
EarthEyes replaces opaque black-box models with transparent, farmer-aligned agro-economic metrics:
1. **Win Rate vs Wheat (%):** Simulating every historical season from 1984 to 2025 to calculate how frequently an alternative crop economically outperforms conventional wheat under dry conditions.
2. **Water Productivity (MAD / m³):** Quantifying real economic value generated per cubic meter of total water consumed (e.g. 3.92 MAD/m³ for chickpea vs < 1.50 MAD/m³ for rainfed wheat).
3. **Biological Nitrogen Fixation Bonus:** Crediting legumes with up to +35 kg N/ha of organic nitrogen fixed into the soil, directly reducing the farmer's synthetic fertilizer costs.
4. **Disease Cycle Interruption:** Penalizing crop families susceptible to soil pathogens identified by TerroirAI's leaf diagnostic system.

### Field-Ready Farmer Interface
Recognizing that satellite data is worthless if rural smallholders cannot understand it, EarthEyes delivers a zero-cognitive-barrier interface in **spoken Moroccan Darija** and French:
- Single button action: *"Quoi planter après ? / شنو نزرع العام جاي ؟"*
- Actionable recommendation cards displaying net margin gains in Dirhams, cubic meters of water saved, and cultural agronomic advice.

### Results & Validated Impact (Meknès Parcel, 33.89°N, -5.55°W)
- **#1 Chickpea (L-7emmez, Legume):** +9,537 MAD/ha net margin, 1,800 m³/ha irrigation water conserved, 74% to 100% win rate over wheat in dry years, and +35 kg natural nitrogen fixed.
- **#2 Early Rustic Barley (Ch3ir, Cereal):** +7,100 MAD/ha net margin, 1,400 m³/ha water saved, 68% win rate, maturing three weeks earlier to escape catastrophic May heatwaves.

---

## 3. NASA Space Agency Data Sources Used
- **NASA POWER API** (Prediction Of Worldwide Energy Resources): Daily precipitation, 2m air temperature, solar radiation, and reference evapotranspiration (ET0) from 1984 through 2025 (41 years).
- **NASA SMAP** (Soil Moisture Active Passive): L3/L4 Surface Volumetric Soil Moisture (0–5 cm depth at 9 km spatial resolution) for seedbed moisture calibration at sowing time.
- **ESA Copernicus Sentinel-2 & MODIS**: Historical NDVI vegetation vigor baselines.
- **ISRIC SoilGrids v2.0**: Global 250m soil texture (clay, sand, organic carbon, pH) for available water holding capacity.

---

## 4. Artificial Intelligence Disclosure
In compliance with the official NASA Space Apps Challenge AI policy:
- Generative AI tools (LLMs) were used strictly for conversational assistance and bilingual translations (French to Moroccan Darija) in `step5_llm`.
- The core crop rotation engine (`step7_rotation`) is a deterministic, open-source mathematical simulation based on agronomic crop water productivity formulas and empirical NASA POWER climate distributions.

---

## 5. 7-Slide Pitch Deck Summary
1. **Slide 1:** Title & Challenge Track (*Help Farmers Adapt to Climate Change*)
2. **Slide 2:** The Crisis: Groundwater depletion (-1.5m/yr) & repeated droughts in Saïss plain
3. **Slide 3:** The Flaw of Status Quo: Why monoculture wheat collapses under current climate
4. **Slide 4:** NASA Data Pipeline: NASA POWER (41-year climate) + NASA SMAP (9km soil moisture)
5. **Slide 5:** The 2-Era Proof: Climate shift (1984–2003 vs 2004–2025) and resilient crop ranking
6. **Slide 6:** Farm Impact: +74% Win Rate, 1,800 m³ water saved/ha, accessible Darija UI
7. **Slide 7:** Transparent Limits & Open Science Roadmap for Morocco
