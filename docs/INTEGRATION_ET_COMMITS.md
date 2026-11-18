# Intégration et publication sur le dépôt de Firas

## 1. Choisir le bon point de départ

La branche consultée est **`firas-interface`** (tout en minuscules, avec un trait d'union). Les changements de ce paquet sont un **complément** à cette branche, pas un remplacement de tout le projet.

Depuis PowerShell dans une copie locale du dépôt :

```powershell
git status                    # vérifier qu'aucun travail non commité n'est perdu
git fetch origin
git switch -c integration-ali origin/firas-interface
```

S'il existe déjà une branche `integration-ali`, utiliser un autre nom, par exemple `integration-ali-v2`. Si des modifications locales non commitées existent, **les enregistrer ou les mettre de côté avant de changer de branche**.

## 2. Copier le paquet

Télécharger `INF1007_LIVRAISON_ALI.zip`, puis décompresser son contenu **directement à la racine du dépôt**, là où se trouve le README de Firas :

```powershell
Expand-Archive -Path "C:\CHEMIN\VERS\INF1007_LIVRAISON_ALI.zip" -DestinationPath . -Force
```

La commande remplace `main.py`, `src/interface.py`, `README.md`, `DECISIONS.md`, `JOURNAL_IA.md` et `requirements.txt` par leurs versions intégrées. **`src/donnees.py`, `src/exceptions.py`, `tests/test_donnees.py`, le CSV et la CI de Firas ne sont PAS fournis dans le ZIP et ne seront pas remplacés.**

## 3. Installer, tester

```powershell
python -m pip install -r requirements.txt
python -m pytest -q
python -m coverage run --source=src -m pytest
python -m coverage report -m
```

Vérifier que `donnees/car_details_v3.csv` est présent. **Reporter dans le README le résultat de couverture obtenu sur le vrai dépôt** (le 68 % de notre simulation n'est pas la mesure finale).

## 4. Entraînement officiel (après validation C)

Présenter à l'auxiliaire cible `selling_price`, RMSE vs référence et forêt aléatoire, puis noter la date dans `DECISIONS.md`. Après approbation :

```powershell
python entrainer_modele.py --validation-c
```

Comparer les scores affichés avec ceux de l'ancien README de Firas et inscrire les **nouveaux scores réels** dans `README.md` et `DECISIONS.md`. Le script produit :

- `modeles/prix_voiture.joblib`
- `modeles/metadonnees.json`

## 5. Vérifier l'interface

```powershell
python main.py
```

Tester :

1. Valeurs numériques et catégories valides → estimation en INR + trait vertical sur l'histogramme ;
2. Saisie numérique vide, non numérique, `NaN`, hors limites → message d'erreur, sans historique ajouté ;
3. Bouton **Voir l'historique** → dernière prédiction affichée ;
4. Fermer et rouvrir l'application → le modèle est chargé sans nouvel entraînement ;
5. Vérifier qu'il y a **9 champs**, sans `mileage` ni `seats`.

## 6. Commiter et pousser

```powershell
git status
git add main.py entrainer_modele.py src/modele.py src/variables_modele.py src/interface.py tests/test_modele.py tests/test_integration_ali.py requirements.txt README.md DECISIONS.md JOURNAL_IA.md docs/
git commit -m "Integrer le modele de prediction a l'interface Tkinter"
git push -u origin integration-ali
```

Après validation C et génération de vrais fichiers du modèle :

```powershell
git add modeles/prix_voiture.joblib modeles/metadonnees.json
git commit -m "Enregistrer le modele valide et les metadonnees"
git push
```

Créer ensuite une **Pull Request vers `main`** à partir de `integration-ali`, relire les changements avec Firas, puis vérifier que la CI GitHub Actions est verte. Les commits d'origine de Firas restent présents dans l'historique puisque la branche d'intégration démarre sur `origin/firas-interface`.

## Attention

- Il n'est pas possible de pousser depuis l'environnement de création du paquet : le push doit se faire depuis un ordinateur ayant accès au dépôt.
- Ne pas prétendre que la validation C/D a eu lieu si l'auxiliaire n'a pas encore été rencontré.
- Une RMSE relevée avant intégration ne garantit pas la RMSE de cette version.
- Signaler à Firas que `src/interface.py` inclut son code et des modifications ciblées pour raccorder ton modèle.
