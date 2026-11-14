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
   - 41-year continuous daily climate series (precipitation, 2m temperature, solar radiation, reference ET0).
   - Proven Saïss trend: **+1.2°C temperature anomaly** and **-22% spring rainfall drop** during the critical grain maturation window.
2. **NASA SMAP (Soil Moisture Active Passive):**
   - High-resolution 9 km L3/L4 surface volumetric soil moisture (0–5 cm depth).
   - Validates sowing readiness in Saïss: benchmarked between **12% and 18%** volumetric water content to prevent false germination.
3. **MODIS & SoilGrids Integration:**
   - Multi-year NDVI phenology tracking merged with local soil physical properties (clay/sand/pH) to adjust Total Available Water (TAW).

---

## Slide 4: The Resilient Rotation Algorithm
Rather than an obscure black-box, TerroirAI ranks crop rotation alternatives using transparent, farmer-aligned agro-economic metrics:
- **Win Rate vs Wheat:** Statistical frequency (% of simulated historic seasons) where the alternative crop outperforms conventional wheat.
- **Water Productivity (MAD / m³):** Real economic value generated per cubic meter of water consumed (e.g., 3.92 MAD/m³ for chickpea vs < 1.50 MAD/m³ for wheat).
- **Nitrogen Fixation Credit:** Biological soil regeneration (+35 kg N/ha for legumes), reducing dependence on costly synthetic fertilizers.
- **Disease & Weed Cycle Disruption:** Breaks cereal-borne root pathogens (*Fusarium*, *Septoria*) identified by the TerroirAI leaf diagnostics module.

---

## Slide 5: Farmer-First Accessible User Experience
- **Zero Jargon:** No satellite coordinates or raw data tables. Farmers receive simple, high-impact recommendation cards.
- **Native Dual Language:** Full support for Moroccan Darija (spoken dialect) and French.
- **Single-Click Decision Support:** *"Chno nezre3 l-3am jay ? / Quoi planter après ?"* delivers immediate actionable rankings.
- **Culturally Tailored Agronomic Advice:**
  - *Chickpea:* "L-7emmez kay-sber l-jeffa o kay-3emmer l-ard b l-azot bla ma techri engrais."
  - *Early Barley:* "Ch3ir kay-wjed bekri qbel ma tji l-7arara dyal Chergui f chher 5."

---

## Slide 6: Validated Agro-Economic & Ecological Impact
Simulated on Saïss soil profiles (Meknès basin, 33.89°N, -5.55°W):
- **Recommendation #1 — Chickpea (L-7emmez, Legume):**
  - **Estimated Gross Margin:** +9,400 MAD / ha (+32% vs rainfed wheat)
  - **Water Productivity:** 3.92 MAD / m³
  - **Win Rate:** Outperforms wheat in **74%** of seasons
  - **Water Saved:** **1,800 m³ / ha** conserved for groundwater recharge
  - **Soil Health:** **+35 kg N / ha** organic nitrogen fixed
- **Recommendation #2 — Early Rustic Barley (Ch3ir, Cereal):**
  - **Estimated Gross Margin:** +7,100 MAD / ha
  - **Water Productivity:** 2.53 MAD / m³
  - **Win Rate:** Outperforms wheat in **68%** of seasons
  - **Water Saved:** **1,400 m³ / ha** conserved
  - **Thermal Escape:** Harvests 3 weeks earlier, escaping May heatwaves

---

## Slide 7: Roadmap, Scientific Integrity & NASA Open Science
- **Strict Hackathon Integrity:** 100% open-source, non-commercial, documented NASA Open Data compliance.
- **Scalable Architecture:** Fast, lightweight FastAPI microservice designed to run on low-bandwidth rural mobile connections with intelligent local caching.
- **Expansion Horizons:** Extending calibration models from Saïss to Tadla, Haouz, and Chaouia agricultural perimeters.
- **Empowering Farmers Today:** Turning NASA space intelligence into livelihood security for Moroccan family farmers.
