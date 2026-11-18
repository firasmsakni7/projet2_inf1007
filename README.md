# Prix d'une voiture d'occasion — Projet 2 INF1007

**Équipe :** Firas Msakni et Ali Mbarek — Polytechnique Montréal, automne 2026.

## Description et domaine

Cette application locale Tkinter estime le **prix de vente d'une voiture d'occasion**, en **roupies indiennes (INR)**, à partir de caractéristiques saisies par un utilisateur. Le bouton **Prédire** affiche l'estimation et sa position sur l'histogramme des prix des voitures du jeu de données. Chaque prédiction réussie est ajoutée dans un **historique CSV** consultable depuis la fenêtre.

**Avertissement :** c'est un exercice pédagogique. L'estimation ne doit pas être utilisée seule pour acheter, vendre ou évaluer réellement un véhicule. Les données sont historiques et concernent le marché indien.

## Jeu de données et licence

- Source : Nehal Birla, [Vehicle dataset from CarDekho (Kaggle)](https://www.kaggle.com/datasets/nehalbirla/vehicle-dataset-from-cardekho).
- Fichier utilisé : `donnees/car_details_v3.csv` (8 128 lignes et 13 colonnes avant nettoyage, selon la fiche de Firas).
- Licence indiquée dans le dépôt d'origine : **Database Contents License (DbCL) v1.0** — [texte de la licence](https://opendatacommons.org/licenses/dbcl/1-0/). Vérifier les conditions de redistribution avant de diffuser le CSV dans le dépôt public.
- Nettoyage (`src/donnees.py`, Firas) : retrait de `torque` et des valeurs manquantes, conversion des colonnes contenant des unités, remplacement de `name` par `marque`, retrait des doublons après transformation.
- Nombre annoncé après nettoyage : 6 698 voitures et 12 colonnes. Ce total est **à reconfirmer par exécution sur le CSV de la branche**.
- Limite de la source : la colonne `mileage` mélange notamment km/l et km/kg ; elle ne fait pas partie des entrées de notre modèle pour éviter une interprétation incorrecte.

## Problème de prédiction et modèle

La **variable cible** est `selling_price` (INR), donc il s'agit d'une **régression**. Neuf caractéristiques sont utilisées :

| Numériques | Catégorielles |
|---|---|
| `year`, `km_driven`, `engine`, `max_power` | `fuel`, `seller_type`, `transmission`, `owner`, `marque` |

Les colonnes `mileage` et `seats` ne sont pas demandées à l'utilisateur. Les colonnes catégorielles sont transformées avec `OneHotEncoder(handle_unknown="ignore")` dans un `Pipeline` scikit-learn. Les valeurs manquantes éventuelles sont traitées dans le pipeline à partir des **données d'entraînement uniquement**.

Modèle proposé : `RandomForestRegressor` (100 arbres, profondeur max. 10, 3 exemples min. par feuille, graine 42). Séparation reproductible 80 % entraînement / 20 % test. Référence : `DummyRegressor(strategy="mean")`, qui prédit la moyenne des prix de l'entraînement. La métrique principale est la **RMSE**, calculée de manière vectorisée avec NumPy ; nous affichons également R².

**Validation C :** cible, métrique et modèle doivent être présentés à l'auxiliaire **avant l'entraînement officiel** ; reporter la date dans `DECISIONS.md`.

### Résultats et limites

Résultats sur les 1 340 voitures de test (graine 42), obtenus avec `python entrainer_modele.py --validation-c` et enregistrés dans `modeles/metadonnees.json` :

| Modèle | RMSE (INR) |
|---|---:|
| Référence (prix moyen) | 506 377 |
| Régression linéaire faite à la main (`src/lineaire.py`) | 259 550 |
| Forêt aléatoire (modèle retenu) | 147 030 |

R² de la forêt : 0,916. La forêt divise l'erreur de la référence par 3,4 ; elle est retenue.

Limites : échantillon ancien et représentatif du marché indien seulement, absence d'informations sur l'état réel des véhicules, annonces de véhicules haut de gamme peu nombreuses, résultats statistiquement sensibles aux valeurs atypiques. Les fourchettes min/max affichées dans l'interface viennent uniquement des données d'entraînement.

## Installation

Python **3.11 ou 3.12** recommandé, avec Tkinter présent (habituellement inclus sous Windows). Exécuter **depuis la racine** du dépôt :

```powershell
python -m pip install -r requirements.txt
python -m pytest
```

Vérifier la présence de `donnees/car_details_v3.csv`. Si le fichier n'est pas présent ou ne peut pas être redistribué, le télécharger depuis la page Kaggle ci-dessus et le placer dans `donnees/` sous ce nom.

**Après validation C uniquement**, produire les deux fichiers sauvegardés :

```powershell
python entrainer_modele.py --validation-c
```

Puis lancer l'interface :

```powershell
python main.py
```

La fenêtre recharge `modeles/prix_voiture.joblib` et `modeles/metadonnees.json` : **elle ne réentraîne pas le modèle**. Ne charger des fichiers `.joblib` que s'ils proviennent du projet ou d'une source de confiance.

## Structure du projet

```text
projet2_inf1007/
├── main.py                       # charge le modèle et affiche Tkinter
├── entrainer_modele.py           # entraînement unique et sauvegarde
├── src/
│   ├── donnees.py                # chargement/nettoyage, variables, historique (Firas)
│   ├── modele.py                 # pipeline, RMSE NumPy, évaluation, prédiction (Ali)
│   ├── variables_modele.py       # adaptateur : JSON -> objets Variable (intégration)
│   ├── exceptions.py             # DonneeInvalideError (Firas)
│   └── interface.py              # Tkinter, champs, résultat, historique, graphique
├── donnees/car_details_v3.csv    # source Kaggle, sous réserve de la licence
├── donnees/historique.csv        # créé par l'application
├── modeles/                     # joblib et JSON produits après entraînement
├── figures/                     # graphique d'exploration savefig (Firas)
├── tests/                       # pytest, dont tests du modèle et de l'interface
├── .github/workflows/tests.yml  # CI pytest à chaque push
├── DECISIONS.md
├── JOURNAL_IA.md
└── requirements.txt
```

## Programmation et qualité du code

- **Chapitre 5** : CSV (données et historique), JSON (métadonnées), chemins avec `os.path`, `with` pour les ouvertures de fichiers.
- **Chapitre 6** : fonctions courtes, annotations de type, docstrings, `return` séparé de l'affichage.
- **Chapitre 7** : le **décorateur `@chronometrer`** utilise `time.perf_counter()` pour mesurer et afficher la durée de la méthode `ModelePrixVoiture.entrainer()`.
- **Chapitre 8** : exception `DonneeInvalideError`, tests `pytest` (cas normaux, limites, erreurs), `pytest.raises` et `pytest.approx`, CI GitHub Actions.
- **Chap. 9–11** : classes `Variable`, `VariableNumerique`, `VariableCategorielle`, `ModelePrixVoiture` et `Application` ; héritage et polymorphisme via `Variable.valider()` ; composition dans `Application`, encapsulation avec attributs `_...`, méthode spéciale `ModelePrixVoiture.__str__()`.
- **Chapitre 12** : calcul vectorisé de la RMSE avec NumPy ; un test compare au calcul scikit-learn.
- **Chapitre 13** : graphique d'exploration `savefig` et histogramme Matplotlib intégré à Tkinter.

## Tests, couverture et CI

Depuis la racine :

```powershell
python -m pytest -q
python -m coverage run -m pytest
python -m coverage report -m
```

Couverture des tests : 70 % sur le code du projet (`src/`), mesurée avec `coverage run -m pytest` puis `coverage report`. `lineaire.py` est à 100 %, `modele.py` à 85 %, `donnees.py` à 63 % et `interface.py` à 38 %, car les fenêtres Tkinter ont été testées à la main (cas normal, saisie invalide, graphique). Les 32 tests passent.
## Documentation officielle consultée

- [pandas — 10 minutes to pandas](https://pandas.pydata.org/docs/user_guide/10min.html)
- [scikit-learn — RandomForestRegressor](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html)
- [scikit-learn — train_test_split](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html)
- [scikit-learn — ColumnTransformer](https://scikit-learn.org/stable/modules/generated/sklearn.compose.ColumnTransformer.html)
- [Matplotlib — Embed in Tk](https://matplotlib.org/stable/gallery/user_interfaces/embedding_in_tk_sgskip.html)
- [Python — Tkinter](https://docs.python.org/3/library/tkinter.html)

## Journal d'IA et décisions

Voir `JOURNAL_IA.md` pour les outils sollicités, les vérifications effectuées et les corrections apportées après test. Voir `DECISIONS.md` pour les choix et les validations de l'auxiliaire. L'équipe doit comprendre et pouvoir expliquer l'ensemble du code présenté, même lorsqu'une IA a contribué à sa rédaction.
