# Journal d'utilisation de l'IA — Projet INF1007

Chaque ligne décrit un usage réel documenté, avec son statut de vérification. La vérification finale sur le vrai CSV et l'intégration GitHub restent à faire.

| Outil | Ce qui a été demandé | Réponse reçue | Vérification effectuée | Décision |
|---|---|---|---|---|
| Claude (Firas) | Structure de dépôt, CI et README | Arborescence et workflow pytest | Exécution et CI annoncée verte sur GitHub par Firas | Gardé |
| Claude (Firas) | Jeux de données de voitures d'occasion | CarDekho et Mendeley | Licence de CarDekho vérifiée manuellement sur Kaggle selon Firas | Gardé |
| Claude (Firas) | Explication de pandas et Matplotlib pour explorer le jeu de données | `read_csv`, `dropna`, `to_numeric`, `scatter`, `savefig` | Figure générée et colonnes contrôlées selon Firas | Gardé |
| Claude (Firas) | Conversion des colonnes avec unités | Utilisation de `to_numeric(errors="coerce")` | Une valeur `"bhp"` n'avait pas de nombre ; ajout d'un second `dropna()` | **Modifié après vérification** |
| ChatGPT (Ali) | Aide pour concevoir un modèle de régression avec baseline, pipeline, RMSE NumPy et sauvegarde JSON/joblib | `ModelePrixVoiture`, fonctions d'évaluation et tests synthétiques | Tests automatisés sur des jeux artificiels ; entraînement officiel sur le vrai CSV **non encore vérifié** | Gardé provisoirement ; à confirmer avec validation C |
| ChatGPT (Ali) | Intégrer le modèle à la branche `firas-interface` sans refaire le travail de Firas | Adapter `Application`, `main.py` et construire les champs à partir du JSON | Relecture du vrai `src/interface.py` : prix fixé temporairement à `0.0` et 11 colonnes UI contre 9 du modèle ; ajout de tests d'intégration | **Modifié après vérification** : remplacement du faux prix, utilisation de 9 champs JSON |
| ChatGPT (Ali) | Compléter la documentation et identifier les vérifications restantes | README, fiche de décisions, commandes d'exécution | Contrôle des éléments demandés dans l'énoncé ; couverture et RMSE définitives laissées à mesurer plutôt qu'inventées | Gardé avec limites explicites |
