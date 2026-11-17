
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline


def rmse_numpy(reels: list[float], predictions: list[float]) -> float:
    """Calcule l'erreur RMSE entre les prix reels et predits.

    Recoit : deux listes de nombres.
    Retourne : la RMSE sous forme d'un float.
    Leve ValueError si les listes sont vides ou incompatibles.
    """
    y_reel = np.asarray(reels, dtype=float)
    y_predit = np.asarray(predictions, dtype=float)

    if y_reel.ndim != 1 or y_predit.ndim != 1:
        raise ValueError("Les entrees doivent etre des vecteurs.")

    if y_reel.size == 0 or y_reel.shape != y_predit.shape:
        raise ValueError("Les listes doivent avoir la meme taille non nulle.")

    if not np.isfinite(y_reel).all() or not np.isfinite(y_predit).all():
        raise ValueError("Les prix doivent etre des nombres finis.")

    erreurs = y_reel - y_predit
    moyenne_carres = np.mean(erreurs ** 2)
    return float(np.sqrt(moyenne_carres))

def separer_donnees(df: pd.DataFrame,cible: str = "selling_price") -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Separe les donnees en ensembles d'entrainement et de test.

    Recoit : un DataFrame nettoye et le nom de la cible.
    Retourne : X_train, X_test, y_train, y_test.
    Leve ValueError si les donnees sont vides ou sans cible.
    """

    if df.empty:
        raise ValueError("Le jeu de donnees est vide.")

    if cible not in df.columns:
        raise ValueError("La colonne cible est introuvable.")

    X = df.drop(columns=[cible])
    y = df[cible]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    return X_train, X_test, y_train, y_test

def modele_reference(y_train: pd.Series, y_test: pd.Series) -> float:
    """Calcule la RMSE d'un modele qui predit toujours le prix moyen.

    Recoit : les prix d'entrainement et de test.
    Retourne : la RMSE du modele de reference.
    Leve ValueError si les donnees sont vides.
    """
    if y_train.empty or y_test.empty:
        raise ValueError("Les donnees ne peuvent pas etre vides.")

    prix_moyen = y_train.mean()

    predictions = np.full(len(y_test), prix_moyen)

    return rmse_numpy(y_test.to_numpy(), predictions)

def entrainer_modele(
    X_train: pd.DataFrame,
    y_train: pd.Series
) -> Pipeline:
    """Entraine une foret aleatoire pour predire le prix des voitures.

    Recoit : les caracteristiques et les prix d'entrainement.
    Retourne : le pipeline entraine.
    Leve ValueError si les donnees sont vides ou incompatibles.
    """
    if X_train.empty or y_train.empty:
        raise ValueError("Les donnees d'entrainement sont vides.")

    if len(X_train) != len(y_train):
        raise ValueError("Les tailles de X et y sont differentes.")

    colonnes_cat = X_train.select_dtypes(
        include=["object", "category"]
    ).columns.tolist()

    colonnes_num = X_train.select_dtypes(
        include="number"
    ).columns.tolist()

    pretraitement = ColumnTransformer(
        transformers=[
            ("categories",
             OneHotEncoder(handle_unknown="ignore"),
             colonnes_cat),
            ("numeriques", "passthrough", colonnes_num)
        ]
    )

    foret = RandomForestRegressor(
        n_estimators=100,
        random_state=42,
        n_jobs=-1
    )

    modele = Pipeline(steps=[
        ("pretraitement", pretraitement),
        ("foret", foret)
    ])

    modele.fit(X_train, y_train)

    return modele
