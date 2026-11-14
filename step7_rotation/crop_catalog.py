"""
Catalogue agronomique des cultures de référence pour la région de Meknès / Saïss.
Les rendements, prix et coûts sont des hypothèses de modélisation paramétrables
fondées sur les données ONICL, FAOSTAT et les pratiques régionales observées.
"""

CROP_CATALOG = {
    "blé": {
        "name_fr": "Blé tendre",
        "name_darija": "L-Gezza (Qme7)",
        "family": "céréale",
        "cycle_days": 160,
        "base_yield_q_ha": 26.0,
        "price_mad_q": 300.0,
        "operational_cost_mad_ha": 4500.0,
        "water_need_m3_ha": 4200.0,
        "drought_sensitivity": 1.15,  # Ky FAO : forte pénalité si stress au remplissage
        "nitrogen_fixation_kg_ha": 0.0,
        "soil_benefit_fr": "Culture de rente traditionnelle, exigeante en eau et azote.",
        "soil_benefit_darija": "Zre3 3adi kay-khdem l-ma bzaf o kay-khwi l-ard men l-azot."
    },
    "pois_chiche": {
        "name_fr": "Pois chiche",
        "name_darija": "L-7emmez",
        "family": "légumineuse",
        "cycle_days": 110,
        "base_yield_q_ha": 16.0,
        "price_mad_q": 850.0,
        "operational_cost_mad_ha": 3800.0,
        "water_need_m3_ha": 2400.0,
        "drought_sensitivity": 0.70,  # Résistant au déficit hydrique
        "nitrogen_fixation_kg_ha": 35.0,
        "soil_benefit_fr": "Fixation naturelle d'azote (+35 kg N/ha) et rupture du cycle des maladies du blé.",
        "soil_benefit_darija": "L-7emmez kay-sber l-jeffa o kay-3emmer l-ard b l-azot bla engrais."
    },
    "orge": {
        "name_fr": "Orge précoce",
        "name_darija": "Ch3ir",
        "family": "céréale_rustique",
        "cycle_days": 125,
        "base_yield_q_ha": 30.0,
        "price_mad_q": 240.0,
        "operational_cost_mad_ha": 2900.0,
        "water_need_m3_ha": 2800.0,
        "drought_sensitivity": 0.80,  # Évite les canicules tardives de mai
        "nitrogen_fixation_kg_ha": 0.0,
        "soil_benefit_fr": "Maturation précoce avant les pics de Chergui printaniers. Paille très valorisée en élevage.",
        "soil_benefit_darija": "Ch3ir kay-wjed bekri qbel ma tji l-7arara dyal Chergui f chher 5."
    },
    "feverole": {
        "name_fr": "Féverole",
        "name_darija": "L-Foul",
        "family": "légumineuse",
        "cycle_days": 140,
        "base_yield_q_ha": 21.0,
        "price_mad_q": 600.0,
        "operational_cost_mad_ha": 3600.0,
        "water_need_m3_ha": 3200.0,
        "drought_sensitivity": 0.85,
        "nitrogen_fixation_kg_ha": 45.0,
        "soil_benefit_fr": "Restructuration des sols argileux lourds et enrichissement massif en azote organique.",
        "soil_benefit_darija": "L-foul kay-fte7 l-ard li fiha l-ghiss o kay-ne99iha men l-mrad."
    },
    "tournesol": {
        "name_fr": "Tournesol de printemps",
        "name_darija": "Nwwar Ch-Chems",
        "family": "oléagineux",
        "cycle_days": 120,
        "base_yield_q_ha": 14.0,
        "price_mad_q": 550.0,
        "operational_cost_mad_ha": 3200.0,
        "water_need_m3_ha": 2900.0,
        "drought_sensitivity": 0.85,
        "nitrogen_fixation_kg_ha": 0.0,
        "soil_benefit_fr": "Enracinement pivotant profond qui valorise l'eau résiduelle du sous-sol.",
        "soil_benefit_darija": "Nwwar ch-chems 3ndo 3rouq twal kay-jebdo l-ma men l-ghreq."
    }
}
