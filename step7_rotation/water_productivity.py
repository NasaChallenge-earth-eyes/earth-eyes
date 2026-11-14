"""
Calcul de la productivité économique de l'eau (FAO Water Productivity)
et des économies hydriques à l'échelle de la parcelle pour le Saïss.
"""

# Prix estimé de l'azote minéral économisé (Urée 46% au Maroc : env. 4.5 MAD / kg N pur)
NITROGEN_VALUE_PER_KG_MAD = 4.50

def calculate_water_productivity(margin_mad_ha: float, water_need_m3_ha: float) -> float:
    """
    Calcule la productivité de l'eau en Dirhams par mètre cube d'irrigation :
    Productivité = Marge Nette (MAD/ha) / Eau consommée (m³/ha)
    """
    if water_need_m3_ha <= 0:
        return 0.0
    return round(margin_mad_ha / water_need_m3_ha, 2)

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
