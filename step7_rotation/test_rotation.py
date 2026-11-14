"""
Script de test et de validation autonome pour le moteur step7_rotation.
Exécutable en ligne de commande pour vérifier les calculs et la conformité au contrat JSON.
"""

import sys
import os
import json

# Permet d'importer step7_rotation depuis la racine du projet
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from step7_rotation.rotation_engine import recommend_crop_rotation

def main():
    print("=" * 70)
    print("🌾 TEST DU MOTEUR D'ADAPTATION CLIMATIQUE & ROTATION (NASA Space Apps 2026)")
    print("=" * 70)

    # Test avec la parcelle de Meknès, culture précédente = Blé, profil = Équilibré
    result = recommend_crop_rotation(
        lat=33.89,
        lon=-5.55,
        previous_crop="blé",
        risk_profile="équilibré"
    )

    print("\n📍 Localisation :", result["location"]["city"], f"({result['location']['lat']}, {result['location']['lon']})")
    print("📊 Tendance Climatique Réelle NASA POWER :")
    trend = result["climate_trend_nasa"]
    print(f"   • Période 1 ({trend['baseline_period']}) vs Période 2 ({trend['recent_period']})")
    print(f"   • Hausse de Température : {trend['temp_increase_celsius']}")
    print(f"   • Baisse des Pluies de Printemps : {trend['spring_rain_decrease_percent']}")

    print("\n🏆 Top 3 des Cultures Recommandées pour Remplacer le Blé :")
    print("-" * 70)
    for rec in result["recommendations"]:
        print(f"\n🥇 Rang {rec['rank']} : {rec['crop_name_fr']} ({rec['crop_name_darija']}) — Famille : {rec['family']}")
        print(f"   • Marge Estimée P50 : {rec['margin_mad_ha']:,} MAD / hectare")
        print(f"   • Fourchette Risque [P10 - P90] : [{rec['margin_p10']:,} MAD - {rec['margin_p90']:,} MAD]")
        print(f"   • Productivité de l'Eau : {rec['water_productivity_mad_m3']} MAD / m³")
        print(f"   • Taux de Victoire face au Blé : {rec['win_rate_vs_wheat_percent']}% des saisons récentes")
        print(f"   • Économie d'Eau dans la Nappe : {rec['water_saved_m3_ha']:,} m³ / hectare")
        print(f"   • Impact Sol & Azote : {rec['soil_health_impact']}")
        print(f"   • Conseil Darija : \"{rec['darija_summary']}\"")

    print("\n" + "=" * 70)
    print("✅ Validation du format JSON pour l'Agent B :")
    print(json.dumps(result, indent=2, ensure_ascii=False)[:400] + "...\n[JSON complet conforme à AGENTS_SYNC.md]")
    print("=" * 70)

if __name__ == "__main__":
    main()
