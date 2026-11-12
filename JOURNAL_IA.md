# Journal d'utilisation de l'IA

| Outil | Ce que nous avons demandé | Réponse reçue | Vérification faite (documentation, test, exécution) | Décision (gardé, modifié, rejeté) |
|---|---|---|---|---|
| Claude | Structure de dépôt de départ (dossiers, CI, README) | Un dossier avec la structure de l'annexe B et un workflow pytest | Test exécuté, CI verte sur GitHub | Gardé |
| Claude | Proposer des jeux de données de voitures d'occasion | CarDekho (Kaggle) et un jeu Mendeley ; licence de CarDekho non vérifiée par Claude | Licence vérifiée nous-mêmes sur Kaggle (DbCL v1.0), df.info() lancé | Gardé (CarDekho) |
| Claude | Apprendre pandas et Matplotlib (non vus en cours) pour charger, nettoyer et explorer le CSV | Explication des méthodes (read_csv, drop_duplicates, drop, dropna, str.split, to_numeric, scatter, savefig) et aide pour écrire les fonctions de donnees.py | Exécution : (6717, 12), types vérifiés avec df.dtypes, image figures/prix_selon_annee.png créée | Gardé |
| Claude | Convertir les colonnes avec unités en nombres | Méthode avec to_numeric(errors="coerce") | L'exécution a montré une valeur « bhp » sans nombre dans max_power : nous avons ajouté un deuxième dropna | Modifié |