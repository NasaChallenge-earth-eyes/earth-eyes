"""
step7_rotation: Moteur d'adaptation climatique et de recommandation de rotation des cultures
développé pour le NASA Space Apps Challenge 2026.
Alimenté par l'API NASA POWER (1984-2025) et les lois de productivité de l'eau FAO.
"""

from .rotation_engine import recommend_crop_rotation

__all__ = ["recommend_crop_rotation"]
