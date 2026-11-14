"""
Calcul de la productivité physique de l'eau (FAO Water Productivity)
et des économies hydriques à l'échelle de la parcelle pour le Saïss (Meknès).
Normes FAO-33, FAO-56 et INRA Maroc.
"""

# Prix indicatif de référence de l'azote minéral économisé (Urée 46% au Maroc : env. 4.5 MAD / kg N pur)
NITROGEN_VALUE_PER_KG_MAD = 4.50

def calculate_water_productivity_kg_m3(yield_kg_ha: float, water_need_m3_ha: float) -> float:
    """
    Calcule la productivité physique de l'eau selon la norme FAO (FAO-33) :
    Productivité = Rendement récolté (kg/ha) / Eau consommée (m³/ha) -> kg de récolte par m³ d'eau.
    """
    if water_need_m3_ha <= 0:
        return 0.0
    return round(yield_kg_ha / water_need_m3_ha, 2)

def calculate_water_productivity(margin_or_yield: float, water_need_m3_ha: float) -> float:
    """
    Compatibilité ascendante : calcule l'efficience par mètre cube d'eau.
    """
    if water_need_m3_ha <= 0:
        return 0.0
    return round(margin_or_yield / water_need_m3_ha, 2)

def calculate_water_saved_vs_baseline(crop_water_m3: float, baseline_water_m3: float = 4200.0) -> float:
    """
    Calcule le volume d'eau préservé dans la nappe phréatique par rapport au blé (m³/ha).
    """
    return max(0.0, round(baseline_water_m3 - crop_water_m3, 1))

def calculate_nitrogen_monetary_bonus(nitrogen_kg_ha: float) -> float:
    """
    Calcule l'économie directe d'engrais azoté minéral pour la saison suivante (MAD/ha).
    """
    return round(nitrogen_kg_ha * NITROGEN_VALUE_PER_KG_MAD, 1)
