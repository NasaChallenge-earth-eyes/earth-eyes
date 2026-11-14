# 🤝 Protocole de Synchronisation Inter-Agents (Antigravity A & B)
# Organisation GitHub : https://github.com/NasaChallenge-earth-eyes
# Projet : EarthEyes / TerroirAI - Climate Adaptation

> [!IMPORTANT]
> **Règle d'or de coordination entre les deux Antigravity :**
> Pour éviter tout conflit de code (`merge conflict`) lors des pushs sur GitHub, **chacun a son périmètre de fichiers exclusif**.
> Un agent ne modifie JAMAIS un fichier appartenant à l'autre sans passer par ce tableau de bord.

---

## 🗺️ 1. Répartition Stricte des Fichiers (File Ownership)

```
earth-eyes/
├── AGENTS_SYNC.md                  # 🔄 PARTAGÉ : Tableau de bord de statut (Pull/Push)
├── NASA_SPACEAPPS_STRATEGY.md      # 📖 PARTAGÉ : Référence stratégique, calculs et pitch
├── HACKATHON_SCOPE.md              # 📖 PARTAGÉ : Déclaration d'intégrité officielle NASA
│
├── [PÉRIMÈTRE DEV A - MOTEUR & DATA NASA]
│   ├── engine/                     # 🟢 EXCLUSIF AGENT A
│   │   ├── __init__.py
│   │   ├── nasa_power_service.py   # Client API NASA POWER + Cache JSON
│   │   ├── crop_catalog.py         # Données agronomiques & prix indicatifs
│   │   ├── water_productivity.py   # Calculs MAD/m³ d'irrigation
│   │   ├── disease_interaction.py  # Matrice pathogène sol / rotation
│   │   ├── rotation_engine.py      # Moteur 2 fenêtres (1984-2003 vs 2004-2025)
│   │   └── test_engine.py          # Validation CLI autonome
│   └── data_cache/                 # 🟢 EXCLUSIF AGENT A : Fichiers JSON hors-ligne
│       └── meknes_power_1984_2025.json
│
├── [PÉRIMÈTRE DEV B - API, UI & PRÉSENTATION]
│   ├── app.py                      # 🔵 EXCLUSIF AGENT B : Serveur FastAPI
│   ├── templates/ & static/        # 🔵 EXCLUSIF AGENT B : Interface Web & affichage des 3 cultures
│   ├── presentation/               # 🔵 EXCLUSIF AGENT B : Slides Pitch (7 slides max en anglais)
│   ├── README.md                   # 🔵 EXCLUSIF AGENT B : Documentation officielle du repo
│   ├── README_EN.md                # 🔵 EXCLUSIF AGENT B : Version anglaise pour le Global Judging
│   └── SUBMISSION_SPACEAPPS.md     # 🔵 EXCLUSIF AGENT B : Textes du formulaire de soumission
```

---

## 📡 2. Le Contrat d'Interface JSON (API Contract)

Pour que l'Agent B puisse construire l'interface web et la route FastAPI **en parallèle** sans attendre l'Agent A, la fonction `recommend_crop_rotation(...)` de l'Agent A renverra obligatoirement ce format de dictionnaire :

```json
{
  "status": "success",
  "location": {
    "city": "Meknès",
    "lat": 33.89,
    "lon": -5.55
  },
  "climate_trend_nasa": {
    "baseline_period": "1984-2003",
    "recent_period": "2004-2025",
    "temp_increase_celsius": "+1.2°C",
    "spring_rain_decrease_percent": "-21.4%"
  },
  "previous_crop": "blé",
  "recommendations": [
    {
      "rank": 1,
      "crop_name_fr": "Pois chiche",
      "crop_name_darija": "L-7emmez",
      "family": "Légumineuse",
      "margin_mad_ha": 9400,
      "water_productivity_mad_m3": 3.92,
      "win_rate_vs_wheat_percent": 74,
      "water_saved_m3_ha": 1800,
      "nitrogen_bonus_kg_ha": 35,
      "soil_health_impact": "Restauration azote et rupture cycle maladies du sol",
      "darija_summary": "L-7emmez kay-sber l-jeffa o kay-3emmer l-ard b l-azot bla engrais."
    },
    {
      "rank": 2,
      "crop_name_fr": "Orge précoce",
      "crop_name_darija": "Ch3ir",
      "family": "Céréale rustique",
      "margin_mad_ha": 7100,
      "water_productivity_mad_m3": 2.53,
      "win_rate_vs_wheat_percent": 68,
      "water_saved_m3_ha": 1400,
      "nitrogen_bonus_kg_ha": 0,
      "soil_health_impact": "Résistance thermique élevée face au Chergui",
      "darija_summary": "Ch3ir kay-wjed bekri qbel ma tji l-7arara dyal Chergui f chher 5."
    }
  ],
  "disclaimer": "Les rendements et marges sont des résultats modélisés sous hypothèses indicatives et ne constituent pas une garantie de récolte."
}
```

---

## 🚦 3. Tableau de Bord de Synchronisation en Direct

*Chaque agent met à jour ce tableau avant de pusher sur GitHub.*

| Tâche | Propriétaire | Statut | Note / Dernière modification |
| :--- | :---: | :---: | :--- |
| Client API NASA POWER + Cache | Agent A | `[FAIT]` | Cache local opérationnel pour Meknès (1984-2025) |
| Remplacement météo WOFOST | Agent A | `[FAIT]` | `nasa_power_weather.py` branché dans `step4_simulation/` |
| Moteur de rotation 2 fenêtres | Agent A | `[FAIT]` | `step7_rotation/` complet, testé via `test_rotation.py` |
| Serveur FastAPI / route rotation | Agent B | `[FAIT]` | `app.py` & `main.py` branchés sur `recommend_crop_rotation` |
| Humidité sol NASA SMAP (0-5cm) | Agent B | `[FAIT]` | `step2_soil/smap_soil.py` opérationnel (calibré 12-18% Saïss) |
| Interface Web (Tableau des 3 cultures) | Agent B | `[FAIT]` | `templates/index.html` avec alerte NASA POWER, SMAP & cartes Darija/FR |
| Slides Pitch (7 slides en anglais) | Agent B | `[FAIT]` | `presentation/SLIDES.md` & deck web interactif sur `/presentation` |
| Documentation soumission NASA | Agent B | `[FAIT]` | `README_EN.md` & `SUBMISSION_SPACEAPPS.md` rédigés |
| Fiche Q&A (Anticipation 5 questions) | Agent A & B | `[À FAIRE]` | Réponses courtes de 20s pour le pitch |

---

## 🔄 4. Protocole Git pour les Deux Agents

Avant chaque intervention :
1. `git pull --rebase origin main` (récupérer les commits de l'autre).
2. Travailler **strictement** dans son dossier attribué.
3. Mettre à jour son statut dans `AGENTS_SYNC.md`.
4. `git add .`
5. `git commit -m "feat: description claire"`
6. `git push origin main`
