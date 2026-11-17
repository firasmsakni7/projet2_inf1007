
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split


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


