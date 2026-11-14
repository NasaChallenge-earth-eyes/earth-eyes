"""
Moteur de décision agronomique de rotation des cultures (NASA Space Apps 2026).
Simule 40 saisons historiques (1984-2025) via NASA POWER, calcule les distributions
de marge (P10, P50, P90), le taux de victoire face au blé (Win Rate), la productivité de l'eau
et l'adaptation topographique anti-érosion (NASA SRTM 30m).
"""

import numpy as np
from typing import Dict, Any, List, Optional

from .nasa_climate_client import NASAClimateClient
from .crop_catalog import CROP_CATALOG
from .water_productivity import (
    calculate_water_productivity,
    calculate_water_saved_vs_baseline,
    calculate_nitrogen_monetary_bonus
)
from .terrain_slope import get_srtm_terrain_profile

def recommend_crop_rotation(
    lat: float = 33.89,
    lon: float = -5.55,
    previous_crop: str = "blé",
    risk_profile: str = "équilibré",
    detected_disease: str = "none",
    slope_pct: Optional[float] = None
) -> Dict[str, Any]:
    """
    Fonction principale de recommandation de rotation culturale sous stress climatique.
    Intègre les données climatiques NASA POWER, l'humidité et la topographie NASA SRTM.
    Renvoie le dictionnaire JSON standard conforme à AGENTS_SYNC.md.
    """
    client = NASAClimateClient(lat, lon)
    climate_analysis = client.analyze_two_eras()

    # Analyse topographique NASA SRTM (Élévation et pente de la parcelle)
    terrain_profile = get_srtm_terrain_profile(lat, lon, user_slope_pct=slope_pct)
    actual_slope = terrain_profile["slope_percent"]

    # Extraction des séries pluviométriques de printemps par année (Mars-Mai)
    params = client.data.get("properties", {}).get("parameter", {})
    rain_dict = params.get("PRECTOTCORR", {})

    spring_rains_by_year = {}
    years = sorted(list(set(k[:4] for k in rain_dict.keys())))
    for y_str in years:
        spring_vals = [v for k, v in rain_dict.items() if (k.startswith(f"{y_str}03") or k.startswith(f"{y_str}04") or k.startswith(f"{y_str}05")) and v != -999.0]
        if spring_vals:
            spring_rains_by_year[y_str] = sum(spring_vals)

    # Référence normale de pluie printanière (médiane sur la série)
    all_spring_rains = list(spring_rains_by_year.values())
    normal_spring_rain = float(np.median(all_spring_rains)) if all_spring_rains else 165.0

    # Simulation année par année de la marge pour le blé (statu quo)
    wheat_info = CROP_CATALOG["blé"]
    wheat_margins_by_year = {}
    for y_str, rain in spring_rains_by_year.items():
        water_stress = max(0.0, 1.0 - (rain / normal_spring_rain))
        realized_yield = wheat_info["base_yield_q_ha"] * max(0.2, 1.0 - (wheat_info["drought_sensitivity"] * water_stress))
        margin = (realized_yield * wheat_info["price_mad_q"]) - wheat_info["operational_cost_mad_ha"]
        wheat_margins_by_year[y_str] = margin

    # Évaluation de chaque culture candidate
    candidates_results = []
    prev_crop_clean = previous_crop.lower().strip()

    for crop_id, crop in CROP_CATALOG.items():
        # Règle anti-monoculture stricte : pas de répétition de la même culture
        if crop_id == prev_crop_clean:
            continue

        margins_all_years = []
        wins_vs_wheat = 0
        total_recent_years = 0

        # Facteur d'adaptation topographique NASA SRTM :
        # Si le terrain est en pente (>3%), les cultures à enracinement profond ou dense
        # valorisent mieux le ruissellement et évitent l'érosion du capital sol
        erosion_prot = crop.get("erosion_protection_score", 1.0)
        slope_adjustment = 1.0
        if actual_slope >= 3.0:
            slope_adjustment = 1.0 + (actual_slope / 100.0) * (erosion_prot - 1.0)

        for y_str, rain in spring_rains_by_year.items():
            water_stress = max(0.0, 1.0 - (rain / normal_spring_rain))
            realized_yield = crop["base_yield_q_ha"] * max(0.25, 1.0 - (crop["drought_sensitivity"] * water_stress))
            margin = (realized_yield * crop["price_mad_q"]) - crop["operational_cost_mad_ha"]

            # Bonus rotation azote si légumineuse
            nitrogen_bonus_mad = calculate_nitrogen_monetary_bonus(crop["nitrogen_fixation_kg_ha"])
            effective_margin = (margin + (nitrogen_bonus_mad * 0.5)) * slope_adjustment

            # Malus sanitaire si la maladie détectée en Step 1 affecte la culture
            if "septoria" in detected_disease.lower() and crop["family"] == "céréale":
                effective_margin *= 0.70  # Malus de 30% si pathogène terricole céréalier

            margins_all_years.append(effective_margin)

            # Win Rate calculé sur la période climatique récente (2004-2025)
            y = int(y_str)
            if y >= 2004:
                total_recent_years += 1
                if effective_margin > wheat_margins_by_year.get(y_str, 0.0):
                    wins_vs_wheat += 1

        win_rate = round((wins_vs_wheat / total_recent_years) * 100) if total_recent_years > 0 else 70

        p10 = float(np.percentile(margins_all_years, 10))
        p50 = float(np.percentile(margins_all_years, 50))
        p90 = float(np.percentile(margins_all_years, 90))

        water_prod = calculate_water_productivity(p50, crop["water_need_m3_ha"])
        water_saved = calculate_water_saved_vs_baseline(crop["water_need_m3_ha"], wheat_info["water_need_m3_ha"])

        candidates_results.append({
            "crop_id": crop_id,
            "crop_name_fr": crop["name_fr"],
            "crop_name_darija": crop["name_darija"],
            "family": crop["family"].capitalize(),
            "margin_p10": round(p10),
            "margin_mad_ha": round(p50),
            "margin_p90": round(p90),
            "water_productivity_mad_m3": water_prod,
            "win_rate_vs_wheat_percent": win_rate,
            "water_saved_m3_ha": int(water_saved),
            "nitrogen_bonus_kg_ha": int(crop["nitrogen_fixation_kg_ha"]),
            "root_type": crop.get("root_type", "moyen"),
            "soil_health_impact": crop["soil_benefit_fr"],
            "darija_summary": crop["soil_benefit_darija"]
        })

    # Classement selon le profil de risque de l'agriculteur
    risk = risk_profile.lower().strip()
    if risk == "prudent":
        candidates_results.sort(key=lambda x: x["margin_p10"], reverse=True)
    elif risk == "ambitieux":
        candidates_results.sort(key=lambda x: x["margin_p90"], reverse=True)
    else:  # équilibré (défaut) : trie sur le P50
        candidates_results.sort(key=lambda x: x["margin_mad_ha"], reverse=True)

    # Attribution des rangs (1, 2, 3...)
    for idx, c in enumerate(candidates_results):
        c["rank"] = idx + 1

    return {
        "status": "success",
        "location": {
            "city": "Meknès",
            "lat": lat,
            "lon": lon
        },
        "climate_trend_nasa": {
            "baseline_period": climate_analysis["era1_period"],
            "recent_period": climate_analysis["era2_period"],
            "temp_increase_celsius": climate_analysis["temp_increase_celsius"],
            "spring_rain_decrease_percent": climate_analysis["spring_rain_decrease_percent"]
        },
        "terrain_srtm": {
            "elevation_m": terrain_profile["elevation_m"],
            "slope_percent": terrain_profile["slope_percent"],
            "erosion_risk": terrain_profile["erosion_risk_fr"],
            "anti_erosion_advice_fr": terrain_profile["anti_erosion_advice_fr"],
            "anti_erosion_advice_darija": terrain_profile["anti_erosion_advice_darija"]
        },
        "previous_crop": previous_crop,
        "risk_profile": risk_profile,
        "recommendations": candidates_results[:3],
        "disclaimer": "Les rendements et marges sont des résultats modélisés sous hypothèses indicatives et ne constituent pas une garantie de récolte."
    }
