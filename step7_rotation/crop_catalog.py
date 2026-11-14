"""
Catalogue agronomique des cultures de référence pour la région de Meknès / Saïss.
Centré sur la physique de production (rendement réel en kg/ha), la santé du sol
à long terme et l'efficience hydrique (FAO, INRA Maroc, ICARDA).
"""

CROP_CATALOG = {
    "blé": {
        "name_fr": "Blé tendre",
        "name_darija": "L-Gezza (Qme7)",
        "family": "céréale",
        "cycle_days": 160,
        "base_yield_kg_ha": 2600.0,      # 26 q/ha en moyenne pluviale Saïss
        "water_need_m3_ha": 4200.0,
        "drought_sensitivity": 1.15,      # Ky FAO-33 : forte pénalité en cas de sécheresse
        "nitrogen_fixation_kg_ha": 0.0,   # Consommateur net d'azote minéral
        "root_type": "fasciculé_superficiel",
        "erosion_protection_score": 1.0,
        "soil_health_score": 35,          # Épuise le sol en monoculture
        "disease_break_capacity": "Nulle (maintient les pathogènes du blé dans le sol)",
        "soil_health_fr": "Monoculture épuisante : dégrade la matière organique et appauvrit l'azote.",
        "soil_health_darija": "L-gezza f l-ard kola 3am kat-3eyyi trab o kat-khwi l-azot kamel."
    },
    "pois_chiche": {
        "name_fr": "Pois chiche",
        "name_darija": "L-7emmez",
        "family": "légumineuse",
        "cycle_days": 110,
        "base_yield_kg_ha": 1600.0,      # 16 q/ha (référentiel INRA Maroc / ICARDA)
        "water_need_m3_ha": 2400.0,      # Très sobre en eau (43% de moins que le blé)
        "drought_sensitivity": 0.70,      # Haute tolérance au stress hydrique
        "nitrogen_fixation_kg_ha": 35.0,  # Fixation symbiotique d'azote de l'air
        "root_type": "pivotant_moyen",
        "erosion_protection_score": 1.15,
        "soil_health_score": 92,          # Régénérateur d'azote majeur
        "disease_break_capacity": "Excellente : casse le cycle de la septoriose et du piétin-verse",
        "soil_health_fr": "Régénérateur de fertilité : enrichit le sol en azote (+35 kg/ha) et assainit la terre.",
        "soil_health_darija": "L-7emmez kay-fiyyeq l-ard : kay-3emmerha b l-azot naturel o kay-ne99iha men l-mrad."
    },
    "orge": {
        "name_fr": "Orge précoce",
        "name_darija": "Ch3ir",
        "family": "céréale_rustique",
        "cycle_days": 125,
        "base_yield_kg_ha": 3000.0,      # 30 q/ha
        "water_need_m3_ha": 2800.0,
        "drought_sensitivity": 0.80,      # Résistance thermique au Chergui printanier
        "nitrogen_fixation_kg_ha": 0.0,
        "root_type": "fasciculé_dense",
        "erosion_protection_score": 1.10,
        "soil_health_score": 60,
        "disease_break_capacity": "Moyenne face aux maladies spécifiques du blé tendre",
        "soil_health_fr": "Rusticité thermique : cycle court évitant les canicules. Paille abondante pour le paillage du sol.",
        "soil_health_darija": "Ch3ir kay-wjed bekri qbel Chergui, o t-teben dyalo kay-ghatti l-ard bach ma t-nchech."
    },
    "feverole": {
        "name_fr": "Féverole",
        "name_darija": "L-Foul",
        "family": "légumineuse",
        "cycle_days": 140,
        "base_yield_kg_ha": 2100.0,      # 21 q/ha
        "water_need_m3_ha": 3200.0,
        "drought_sensitivity": 0.85,
        "nitrogen_fixation_kg_ha": 45.0,  # Fixation record d'azote biologique
        "root_type": "pivotant_dense",
        "erosion_protection_score": 1.25,
        "soil_health_score": 95,          # Meilleure note agronomique pour sols lourds
        "disease_break_capacity": "Totale : rupture complète des cycles parasitaires des céréales",
        "soil_health_fr": "Restructuration biologique : aère les sols argileux lourds et apporte +45 kg N/ha d'azote.",
        "soil_health_darija": "L-foul kay-fte7 l-ard l-ghliya b l-3rouq dyalo o kay-khelli fiha l-khir dyal l-azot."
    },
    "tournesol": {
        "name_fr": "Tournesol de printemps",
        "name_darija": "Nwwar Ch-Chems",
        "family": "oléagineux",
        "cycle_days": 120,
        "base_yield_kg_ha": 1400.0,      # 14 q/ha
        "water_need_m3_ha": 2900.0,
        "drought_sensitivity": 0.85,
        "nitrogen_fixation_kg_ha": 0.0,
        "root_type": "pivotant_profond",
        "erosion_protection_score": 1.35, # Enracinement pivotant profond anti-érosion
        "soil_health_score": 75,
        "disease_break_capacity": "Excellente : famille totalement différente des céréales et légumineuses",
        "soil_health_fr": "Décompactage et ancrage : racine pivot de 1.5m qui puise l'eau profonde et stoppe l'érosion.",
        "soil_health_darija": "Nwwar ch-chems 3ndo 3erq twil kay-hfrou l-ard f l-ghreq o kay-ched trab f l-hadra."
    }
}
