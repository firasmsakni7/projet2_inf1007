# Prix d'une voiture d'occasion — Projet 2 INF1007

**Équipe :** Firas Msakni, Ali Mbarek

## Description
Application qui **estime le prix de vente d'une voiture d'occasion** à partir de ses caractéristiques
(année, kilométrage, carburant, boîte de vitesses, puissance, marque…).
L'utilisateur remplit un formulaire, clique sur « Prédire » et obtient un prix estimé en roupies indiennes,
avec un graphique qui situe sa voiture parmi les prix du jeu de données.
Chaque prédiction est enregistrée dans un historique consultable depuis l'application.

## Jeu de données
- **Source :** « Vehicle dataset from CarDekho », par nehalbirla (Kaggle),
  https://www.kaggle.com/datasets/nehalbirla/vehicle-dataset-from-cardekho
- **Fichier :** `donnees/car_details_v3.csv` (8 128 lignes, 13 colonnes)
- **Licence :** Database Contents License (DbCL) v1.0, https://opendatacommons.org/licenses/dbcl/1-0/
- **Après nettoyage :** 6 698 voitures, 12 colonnes. Les décisions de nettoyage sont expliquées dans `DECISIONS.md`.

## Installation et lancement
```
pip install -r requirements.txt
python main.py
```
Lancer les commandes depuis la racine du dépôt (le dossier qui contient ce README).

## Structure du code
```
projet2_inf1007/
├── main.py                 # point d'entrée : charge les données et lance l'interface
├── src/
│   ├── donnees.py          # lecture, nettoyage, graphique d'exploration, classes de variables, historique
│   ├── modele.py           # séparation, référence, forêt aléatoire, RMSE, sauvegarde, prédiction
│   ├── exceptions.py       # DonneeInvalideError
│   └── interface.py        # interface graphique Tkinter (classe Application)
├── tests/                  # tests pytest
├── donnees/                # jeu de données CSV
├── modeles/                # modèle sauvegardé (joblib) et métadonnées
└── figures/                # graphique d'exploration
```

**Programmation orientée objet**
- **Héritage et polymorphisme :** `Variable` (classe parente) → `VariableNumerique` et `VariableCategorielle`.
  Chaque classe enfant redéfinit `valider(saisie)` : la première vérifie un nombre dans un intervalle,
  la seconde une valeur dans une liste. L'interface appelle `variable.valider(texte)` sans savoir de quelle classe il s'agit.
- **Composition :** `Application` contient la liste des variables, le modèle et le graphique.
- **Encapsulation :** attributs protégés (`_nom`, `_minimum`, `_valeurs`…) et propriétés en lecture seule (`@property`).
- **Exception personnalisée :** `DonneeInvalideError`, levée par `valider` et affichée dans un message clair
  (aucun plantage ni traceback dans l'interface).

## Résultat du modèle
- **Cible :** `selling_price` (prix de vente, en roupies) : problème de **régression**.
- **Modèle :** forêt aléatoire (`RandomForestRegressor`, 100 arbres), variables catégorielles encodées (one-hot).
- **Séparation :** 80 % entraînement, 20 % test, graine fixée (`random_state=42`).
- **Métrique :** RMSE (erreur quadratique moyenne, en roupies), calculée avec NumPy.

| Modèle | RMSE sur l'ensemble de test |
|---|---|
| Référence (prédit toujours le prix moyen) | 506 377 roupies |
| Forêt aléatoire | 144 243 roupies |

La forêt fait environ **3,5 fois moins d'erreur** que la référence.
**Limites :** le prix réel dépend aussi de l'état de la voiture, qui n'est pas dans les données ;
les voitures de luxe (plus de 2 000 000 roupies) sont rares, donc moins bien prédites ;
la colonne `mileage` mélange deux unités (kmpl et km/kg pour le gaz).

## Tests
```
pytest
coverage run -m pytest
coverage report -m
```
**Couverture obtenue :** À COMPLÉTER (48 % avant l'ajout des tests du modèle et des classes de variables).

## Outil du chapitre 7 utilisé
À COMPLÉTER : par exemple, « un décorateur `@chronometrer` mesure et affiche la durée de l'entraînement du modèle ».

## Documentation consultée
- pandas : *10 minutes to pandas*, https://pandas.pydata.org/docs/user_guide/10min.html
- scikit-learn : *RandomForestRegressor*, https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html
- scikit-learn : *train_test_split*, https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html
- Tkinter : https://docs.python.org/3/library/tkinter