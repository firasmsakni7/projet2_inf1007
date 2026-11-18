# Compte rendu des vérifications — version intégrée

## Vérifications effectuées

L'assemblage a été vérifié en utilisant les **fichiers `donnees.py`, `exceptions.py` et `test_donnees.py` transcrits depuis la branche publique `firas-interface`**, ainsi que les nouvelles parties Ali.

- 27 tests pytest réussis : 16 tests du modèle, 7 tests de raccordement et 4 tests de Firas.
- Entraînement **de simulation** sur un CSV synthétique de 8 128 lignes avec les 13 colonnes CarDekho ; sauvegarde et rechargement `.joblib` + `.json` réussis.
- Test en fenêtre Tkinter virtuelle (`xvfb`) : 9 champs ; bouton Prédire → valeur non nulle ; historique écrit ; graphique initialisé.
- Couverture mesurée **en simulation seulement** : 68 % sur `src/` (avec `coverage run --source=src -m pytest`).

**NE PAS REPORTER** les scores de RMSE de la simulation comme résultats de votre projet : ils n'ont aucune signification sur les prix réels. Ils sont volontairement exclus du README principal.

## À confirmer sur le vrai dépôt (non effectué ici)

- Exécution de `python -m pytest -q` sur le **vrai** CSV `donnees/car_details_v3.csv`.
- Réunion / validation C (et validation D pour Tkinter + maquette) auprès de l'auxiliaire.
- Entraînement officiel, sauvegarde du modèle et métriques réelles.
- Lancement sur Windows avec affichage réel et essais des saisies invalides.
- Couverture réelle, à inscrire dans le README.
- Push dans votre dépôt et statut vert de GitHub Actions après intégration.
- Démo chronométrée à deux, avec capture d'écran comme plan de secours.

## Important

Aucune modification du dépôt GitHub distant n'a été effectuée depuis cet environnement. Le paquet est un **ensemble de fichiers à intégrer** à la branche `firas-interface`.
