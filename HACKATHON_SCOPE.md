# ⚖️ Déclaration de Périmètre du Hackathon (Hackathon Scope & Integrity)
# NASA Space Apps Challenge 2026 — Meknès Local & Global
# Organisation GitHub : https://github.com/NasaChallenge-earth-eyes
# Projet : EarthEyes / TerroirAI Climate

Conformément au règlement officiel du **NASA Space Apps Challenge 2026** concernant l'intégrité, l'originalité des travaux et l'utilisation de briques open-source antérieures :

---

## 1. Travaux Préexistants (Recherche & Briques Open Source Antérieures)
Les éléments suivants sont issus de travaux académiques ou de bibliothèques tierces préexistantes et sont réutilisés comme composants de référence :
* Modèles CNN de diagnostic de maladies foliaires (issus du dépôt académique TerroirAI sous licence libre).
* Principes généraux d'interrogation de Google Earth Engine et SoilGrids.

---

## 2. Travaux Nouveaux Développés EXCLUSIVEMENT Pendant le Hackathon (14-15 Nov 2026)
L'intégralité des fonctionnalités ci-dessous a été conçue, modélisée, codée et testée **durant les 48 heures officielles du hackathon** pour répondre au défi *Adapting Farms with NASA Data* :
* **Ingestion de l'API NASA POWER (1984–2025) :** Pipeline de requêtage, nettoyage et mise en cache locale des séries agroclimatiques journalières pour Meknès (`lat=33.89, lon=-5.55`).
* **Analyse Comparative des Deux Fenêtres Climatiques (1984–2003 vs 2004–2025) :** Démonstration chiffrée du réchauffement (+1.2°C) et de la rupture pluviométrique au Saïss.
* **Moteur Décisionnel de Rotation Culturale (`engine/`) :** Algorithme multicritère calculant pour chaque culture candidate :
  * Le rendement probable sous stress hydrique.
  * La marge économique nette en Dirhams par hectare (MAD/ha).
  * La métrique standard de productivité de l'eau FAO en **Dirhams par mètre cube d'irrigation** ($\text{MAD}/m^3$).
  * Le **Taux de Victoire face au statu quo (Win Rate %)** sur 40 saisons simulées.
* **Interface Utilisateur & Traduction Darija :** Tableau de bord web responsive et assistant adapté aux agriculteurs locaux.
* **Présentation & Documentation :** Pitch deck officiel de 7 slides en anglais et dossier de soumission.

---

## 3. Données des Agences Spatiales Utilisées
* **NASA POWER API** (Agroclimatologie, radiation solaire, précipitations et températures journalières).
* **ESA Copernicus Sentinel-2** (Indice de végétation NDVI).
* **FAO GAEZ / FAO-56** (Enveloppes agro-écologiques et modélisation de la productivité de l'eau).
