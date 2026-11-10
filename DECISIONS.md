# Fiche de decisions

| Choix | Options envisagees | Choix retenu et justification | Valide par l'auxiliaire (date) |
|---|---|---|---|
| Domaine | Coupe du monde, location de velos, voitures d'occasion | Voitures d'occasion : cible numerique claire, application utile pour acheter ou vendre une voiture | Samuelle St-Onge, 9 novembre 2026 (Discord) |
| Jeu de donnees | CarDekho (Kaggle), jeu Mendeley (prix en taka, ecrits en texte) | CarDekho car_details_v3.csv : 8 128 lignes, variables numeriques et categorielles, licence DbCL v1.0, aucune donnee personnelle | Samuelle St-Onge, 9 novembre 2026 (Discord) |
| Cible et metrique | | | |
| Modele | | | |
| Technologie d'interface | | | |
| Nettoyage des données | Garder ou retirer les doublons, torque, les lignes incomplètes ; garder name ou en extraire la marque | 1) Retirer les 1 202 doublons : une même voiture ne doit pas être à la fois dans l'entraînement et le test. 2) Retirer torque : trop de formats différents (« 190Nm@ 2000rpm », « 22.4 kgm at… »). 3) Retirer les lignes incomplètes (environ 220, moins de 3 %). 4) Convertir mileage, engine et max_power en nombres en retirant l'unité ; une valeur sans nombre (« bhp ») devient manquante et sa ligne est retirée. 5) Remplacer name par la marque (31 valeurs au lieu de plusieurs milliers). Résultat : 6 717 lignes, 12 colonnes. Limite : mileage mélange kmpl et km/kg (gaz). | |