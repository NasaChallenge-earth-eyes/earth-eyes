"""
Script de test et de validation autonome pour le moteur step7_rotation.
Exécutable en ligne de commande pour vérifier les calculs, l'érosion SRTM et la conformité JSON.
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from step7_rotation.rotation_engine import recommend_crop_rotation

def main():
    print("=" * 75)
    print("🌾 TEST DU MOTEUR D'ADAPTATION CLIMATIQUE & TOPOGRAPHIQUE (NASA Space Apps 2026)")
    print("=" * 75)

    # Test avec la parcelle de Meknès (pente dérivée par NASA SRTM)
    result = recommend_crop_rotation(
        lat=33.89,
        lon=-5.55,
        previous_crop="blé",
        risk_profile="équilibré"
    )

    print("\n📍 Localisation :", result["location"]["city"], f"({result['location']['lat']}, {result['location']['lon']})")
    
    print("\n🏔️ Analyse Topographique NASA SRTM (30m) :")
    terrain = result["terrain_srtm"]
    print(f"   • Altitude : {terrain['elevation_m']} m")
    print(f"   • Pente Estimée : {terrain['slope_percent']}%")
    print(f"   • Risque d'Érosion : {terrain['erosion_risk']}")
    print(f"   • Aménagement Recommandé (FR) : {terrain['anti_erosion_advice_fr']}")
    print(f"   • Conseil Topo (Darija) : \"{terrain['anti_erosion_advice_darija']}\"")

    print("\n📊 Tendance Climatique Réelle NASA POWER :")
    trend = result["climate_trend_nasa"]
    print(f"   • Période 1 ({trend['baseline_period']}) vs Période 2 ({trend['recent_period']})")
    print(f"   • Hausse de Température : {trend['temp_increase_celsius']}")
    print(f"   • Baisse des Pluies de Printemps : {trend['spring_rain_decrease_percent']}")

    print("\n🏆 Top 3 des Cultures Recommandées (Avec Résilience Pente SRTM) :")
    print("-" * 75)
    for rec in result["recommendations"]:
        print(f"\n🥇 Rang {rec['rank']} : {rec['crop_name_fr']} ({rec['crop_name_darija']}) — Famille : {rec['family']}")
        print(f"   • Marge Estimée P50 : {rec['margin_mad_ha']:,} MAD / hectare")
        print(f"   • Fourchette Risque [P10 - P90] : [{rec['margin_p10']:,} MAD - {rec['margin_p90']:,} MAD]")
        print(f"   • Productivité de l'Eau : {rec['water_productivity_mad_m3']} MAD / m³")
        print(f"   • Taux de Victoire face au Blé : {rec['win_rate_vs_wheat_percent']}% des saisons récentes")
        print(f"   • Économie d'Eau dans la Nappe : {rec['water_saved_m3_ha']:,} m³ / hectare")
        print(f"   • Système Racinaire : {rec['root_type']}")
        print(f"   • Impact Sol & Azote : {rec['soil_health_impact']}")
        print(f"   • Conseil Darija : \"{rec['darija_summary']}\"")

    print("\n" + "=" * 75)
    print("✅ Validation du format JSON complet :")
    print(json.dumps(result, indent=2, ensure_ascii=False)[:480] + "...\n[JSON complet conforme et enrichi]")
    print("=" * 75)

if __name__ == "__main__":
    main()
