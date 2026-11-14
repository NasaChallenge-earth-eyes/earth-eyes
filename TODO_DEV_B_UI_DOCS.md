# 🎨 Feuille de Route Personnelle — DEV B & Antigravity B
# Rôle : Lead API, Interface Utilisateur & Présentation Hackathon
# Organisation GitHub : https://github.com/NasaChallenge-earth-eyes
# Projet : EarthEyes / TerroirAI Climate

> [!NOTE]
> Vous êtes responsable de la couche visible : l'API FastAPI, l'interface web pour l'agriculteur, les slides de pitch et la documentation pour le jury mondial de la NASA.
> Vous consommez le contrat JSON défini dans `AGENTS_SYNC.md` sans dépendre de l'avancement de l'Agent A.

---

## 🛠️ Vos Fichiers Dédiés (Périmètre Exclusif)
Vous travaillez **uniquement** dans :
* `app.py` (Serveur FastAPI)
* `templates/` et `static/` (Interface Web)
* `presentation/` (Slides du pitch)
* `README.md` et `README_EN.md`
* `SUBMISSION_SPACEAPPS.md`

---

## 📋 Vos Tâches Prioritaires (Par ordre chronologique)

### Tâche 1 : Mock & Serveur FastAPI `app.py` (30 min)
- [ ] Créer `app.py` avec FastAPI :
  - Définir la route `POST /recommend-rotation`
  - Créer un mock temporaire renvoyant exactement le JSON d'exemple spécifié dans `AGENTS_SYNC.md` (pour pouvoir développer l'interface immédiatement).
  - Quand l'Agent A aura terminé, il suffira de remplacer le mock par :
    ```python
    from engine.rotation_engine import recommend_crop_rotation
    ```

### Tâche 2 : Interface Web Intuitive pour l'Agriculteur (1h)
- [ ] Créer `templates/index.html` (avec Tailwind CSS ou CSS simple) :
  - Formulaire simple : Choix de la ville (Meknès par défaut), culture précédente (Blé par défaut), profil de risque (*Prudent*, *Équilibré*, *Ambitieux*).
  - Bouton : **« Quoi planter après ? / Chno nezre3 l-3am jay ? »**
  - Section Résultats :
    - Carte d'alerte climatique NASA POWER (hausse T° et baisse pluie).
    - 3 cartes pour les 3 meilleures cultures (Rang 🥇, 🥈, 🥉) avec :
      - Nom en français et en **Darija**
      - Marge nette estimée en **MAD/ha**
      - Productivité de l'eau en **MAD/m³**
      - Volume d'eau économisé ($m^3$)
      - Conseil agronomique en Darija
    - Mention de transparence : *"Modélisation basée sur 40 ans de données NASA POWER et lois agronomiques FAO"*.

### Tâche 3 : Slides Pitch (Format Officiel NASA : 7 Slides Max) (1h)
- [ ] Préparer les 7 diapositives en anglais (dans `presentation/`) :
  - **Slide 1 - Title :** EarthEyes — Climate-Adaptive Crop Rotation with NASA Data for Meknès.
  - **Slide 2 - The Crisis :** Groundwater depletion (ABHS data: -1.5m/yr) & repeated droughts in Saïss plain.
  - **Slide 3 - The Flaw of Status Quo :** Why monoculture wheat fails under the new climate.
  - **Slide 4 - NASA Data Pipeline :** NASA POWER (40-yr climate) + Sentinel-2 + FAO Crop Water Productivity.
  - **Slide 5 - The 2-Era Proof :** Climate comparison (1984-2003 vs 2004-2025) showing the shift in best crop.
  - **Slide 6 - Farm Impact :** +74% Win Rate, 1,800 m³ water saved/ha, accessible Darija UI.
  - **Slide 7 - Transparent Limits & Next Steps :** Scientific honesty (assumptions, local calibration).

### Tâche 4 : Documentation & Soumission Globale NASA (45 min)
- [ ] Créer `README_EN.md` et `SUBMISSION_SPACEAPPS.md` :
  - Titre du projet, description courte (2-3 phrases).
  - Liste explicite des données d'agences spatiales utilisées (**NASA POWER API**, **ESA Copernicus Sentinel-2**).
  - Déclaration d'utilisation des outils IA (obligatoire dans le règlement).
- [ ] Mettre à jour `AGENTS_SYNC.md` (`Statut : [FAIT]`) et faire `git commit` + `git push`.
