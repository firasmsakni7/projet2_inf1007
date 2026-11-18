# Comprendre et présenter votre Projet INF1007

## La chaîne complète

**CSV Kaggle** → Firas : `charger_donnees()` / `nettoyer_donnees()` → Ali : `ModelePrixVoiture.entrainer()` (train/test, encodage catégoriel, forêt aléatoire, comparaison à la moyenne, RMSE NumPy) → fichiers **joblib + JSON** → `main.py` charge les fichiers → `construire_variables_metadonnees()` crée les objets `Variable` depuis le JSON → l'utilisateur saisit ses 9 caractéristiques → `Application._predire()` appelle `ModelePrixVoiture.predire()` → affichage du prix INR, graphique et historique CSV.

**Ne jamais confondre entraînement et prédiction.** L'entraînement apprend les relations entre colonnes et prix ; la prédiction utilise le modèle déjà calculé sur une nouvelle ligne de caractéristiques.

## Ton module `src/modele.py`, expliqué par parties

- **Constantes** : `CIBLE = "selling_price"`, quatre colonnes numériques et cinq catégorielles, graine 42. On n'utilise pas la colonne cible comme entrée.
- **`chronometrer()`** : décorateur qui affiche la durée d'entraînement avec `perf_counter()`. Il ne change pas la valeur renvoyée.
- **`rmse_numpy()`** : NumPy calcule `sqrt(mean((y_reel - y_predit)**2))` sans boucle Python. La RMSE est en roupies indiennes. Plus elle est petite, plus les écarts sont petits ; elle ne représente PAS une précision en pourcentage.
- **`ModelePrixVoiture`** : classe avec `_pipeline` et `_metadonnees` protégés. Sa méthode `__str__()` indique si elle est entraînée.
- **`_creer_pipeline()`** : imputations numériques/catégorielles + `OneHotEncoder` + `RandomForestRegressor` (100 arbres). Le pipeline garantit les mêmes transformations à l'entraînement et à la prédiction.
- **`entrainer()`** : filtre les prix invalides, sépare le jeu en 80/20, ajuste uniquement sur le train, évalue sur le test, compare à `DummyRegressor` qui prédit la moyenne du train, construit les bornes des variables et histogramme, mémorise les métriques.
- **`predire()`** : valide le dictionnaire de neuf caractéristiques, convertit les nombres, rejette les catégories non reconnues et retourne une estimation en INR.
- **`sauvegarder()` / `charger()`** : stockent et restaurent le pipeline (`joblib`) et les variables/métriques (`JSON`). Le programme ne réentraîne pas à chaque ouverture.

## Trois problèmes importants corrigés en intégration

1. Firas avait `prix = 0.0` en attendant ton travail. Maintenant `_predire()` appelle réellement ton modèle.
2. La fonction originale `construire_variables(df)` affichait 11 entrées alors que le modèle en utilise 9. Le nouvel adaptateur `construire_variables_metadonnees()` construit les 9 bonnes entrées depuis `metadonnees.json`.
3. Le fichier `main.py` original chargeait les données puis lançait l'interface sans modèle. Maintenant il charge le `.joblib` et le `.json` avant de lancer Tkinter.

## Exemple de déroulement oral (5 minutes de présentation à deux)

- **0:00–0:45 (Firas)** : contexte, voiture d'occasion, source Kaggle, variable cible et utilisateurs.
- **0:45–1:45 (Ali)** : régression, forêt aléatoire, entrée numérique/catégorielle, 80/20, référence et RMSE **réelles à insérer**.
- **1:45–3:15 (Firas + Ali)** : démonstration d'une saisie valide, d'une saisie erronée, du graphique, de l'historique.
- **3:15–4:15 (Ali)** : schéma des fichiers et POO, héritage `Variable` et classe `ModelePrixVoiture`, composition dans `Application`, JSON/joblib.
- **4:15–5:00 (ensemble)** : difficultés, limites, vérifications, IA déclarée.

## Questions possibles et réponses courtes

**Pourquoi la RMSE ?** Parce que le prix est numérique et la RMSE exprime l'erreur en roupies, en pénalisant davantage les écarts importants.

**Pourquoi `random_state=42` ?** Pour obtenir une séparation et un comportement aléatoire reproductibles ; le nombre 42 est arbitraire.

**Pourquoi ne pas entraîner sur 100 % des données ?** Sinon on ne pourrait pas évaluer honnêtement les performances sur des observations jamais vues.

**Pourquoi `OneHotEncoder` ?** Une forêt de scikit-learn attend des valeurs numériques ; chaque catégorie devient une variable indicatrice. On évite de donner un ordre numérique arbitraire aux carburants ou marques.

**Pourquoi une référence ?** Une forêt doit faire mieux qu'une stratégie triviale (prédire toujours la moyenne) pour qu'un résultat soit réellement intéressant.

**Pourquoi JSON + joblib ?** `joblib` sauvegarde l'objet scikit-learn ; JSON conserve les informations nécessaires pour construire les champs et afficher les métriques. On charge les deux sans refaire l'entraînement.

**Où sont les principes de POO ?** `Variable` est la classe parente, `VariableNumerique` et `VariableCategorielle` redéfinissent `valider()` ; `Application` contient ces variables et le modèle ; `ModelePrixVoiture.__str__` est une méthode spéciale.

**Pourquoi seulement neuf champs ?** `mileage` a des unités mélangées (km/l et km/kg) et `seats` a été écartée pour simplifier l'interface ; les choix sont consignés dans `DECISIONS.md`.

**Quelles limites ?** Prix indiens historiques, description imparfaite de l'état des véhicules, prédictions plus incertaines pour exemples rares et extrêmes, valeur de la RMSE à vérifier sur le vrai jeu de test.

**IA utilisée ?** Oui : aide à concevoir et tester le code et à vérifier l'intégration ; tout est déclaré dans `JOURNAL_IA.md`, et les résultats non vérifiés n'ont pas été présentés comme définitifs.
