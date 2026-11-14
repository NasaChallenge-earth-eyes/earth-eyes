# 🎯 Feuille de Route Personnelle — DEV A & Antigravity A
# Rôle : Lead Data NASA & Moteur Agroclimatique
# Organisation GitHub : https://github.com/NasaChallenge-earth-eyes
# Projet : EarthEyes / TerroirAI Climate

> [!NOTE]
> Vous êtes responsable du cœur algorithmique et de l'ingestion des données spatiales de la NASA.
> Votre travail alimente directement l'Agent B via le contrat JSON défini dans `AGENTS_SYNC.md`.

---

## 🛠️ Vos Fichiers Dédiés (Périmètre Exclusif)
Vous travaillez **uniquement** dans :
* `engine/` (tous les fichiers de calcul)
* `data_cache/` (fichiers JSON)
* `HACKATHON_SCOPE.md`

---

## 📋 Vos Tâches Prioritaires (Par ordre chronologique)

### Tâche 1 : Intégrité Hackathon (10 min)
- [ ] Créer le fichier `HACKATHON_SCOPE.md` qui liste :
  - **Existant (projet de recherche antérieur / open-source) :** Références aux modèles CNN et architectures génériques.
  - **Développé pendant le Hackathon NASA Space Apps 2026 :** Moteur `engine/` complet, client NASA POWER 1984-2025, calculs de productivité de l'eau ($MAD/m^3$), Win Rate multi-décennal et adaptation aux 2 fenêtres climatiques.

### Tâche 2 : Client NASA POWER & Cache Local Hors-Ligne (30 min)
- [ ] Créer `engine/nasa_power_service.py` :
  - Interroger l'API REST : `https://power.larc.nasa.gov/api/temporal/daily/point`
  - Coordonnées de Meknès : `lat=33.89, lon=-5.55`
  - Période : `19840101` à `20251231` (pour éviter l'année 2026 incomplète)
  - Paramètres : `T2M, T2M_MAX, T2M_MIN, PRECTOTCORR, ALLSKY_SFC_SW_DWN, RH2M`
  - Sauvegarder la réponse brute dans `data_cache/meknes_power_1984_2025.json` pour que le projet fonctionne **100% hors-ligne en cas de coupure Wi-Fi**.

### Tâche 3 : Catalogue Agronomique & Productivité de l'Eau (30 min)
- [ ] Créer `engine/crop_catalog.py` :
  - Définir le dictionnaire des cultures marocaines avec données chiffrées (étiquetées comme hypothèses paramétrables) :
    - *Blé (statu quo)* : 4 200 m³ d'eau, 300 MAD/q, 4 500 MAD/ha charges.
    - *Pois chiche (Homs)* : 2 400 m³ d'eau, 850 MAD/q, 3 800 MAD/ha charges, +35 kg N/ha.
    - *Orge précoce (Ch3ir)* : 2 800 m³ d'eau, 240 MAD/q, 2 900 MAD/ha charges.
    - *Féverole (Foul)* : 3 200 m³ d'eau, 600 MAD/q, 3 600 MAD/ha charges, +45 kg N/ha.
- [ ] Créer `engine/water_productivity.py` :
  - Calculer la formule FAO : $\text{Productivité} = \frac{\text{Marge (MAD)}}{\text{Consommation d'eau } (m^3)}$.
  - Calculer l'économie d'eau par rapport au blé ($m^3/ha$).

### Tâche 4 : Moteur 2 Fenêtres Climatiques & Win Rate (45 min)
- [ ] Créer `engine/rotation_engine.py` :
  - Découper la série temporelle en 2 blocs :
    - **Fenêtre 1 (1984 - 2003)** : Période historique.
    - **Fenêtre 2 (2004 - 2025)** : Période de changement climatique accéléré.
  - Calculer la vraie hausse de température et la vraie baisse des pluies de printemps pour Meknès.
  - Simuler les rendements et marges annuelles pour chaque culture.
  - Calculer le **Win Rate réel** (% d'années où le pois chiche ou l'orge bat le blé).
  - Exposer la fonction principale :
    ```python
    def recommend_crop_rotation(lat: float, lon: float, previous_crop: str = "blé", risk_profile: str = "équilibré") -> dict:
        # Renvoie le dictionnaire JSON conforme à AGENTS_SYNC.md
    ```

### Tâche 5 : Test et Validation Autonome (15 min)
- [ ] Créer et exécuter `engine/test_engine.py` :
  - Vérifier que la fonction s'exécute en < 1 seconde grâce au cache JSON.
  - Noter les vrais chiffres obtenus (hausse T°, baisse pluie %, Win Rate %) pour les transmettre à l'Agent B.
- [ ] Mettre à jour `AGENTS_SYNC.md` (`Statut : [FAIT]`) et faire `git commit` + `git push`.
