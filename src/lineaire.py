import numpy as np
import pandas as pd


def preparer_matrice(df: pd.DataFrame, cible: str = "selling_price") -> tuple[pd.DataFrame, pd.Series]:
    """Prépare les données pour la régression linéaire faite à la main.

    Reçoit : le tableau nettoyé et le nom de la colonne cible.
    Retourne : X, où chaque colonne texte devient des colonnes de 0 et 1,
    et y, la colonne cible.
    Lève ValueError si la cible n'est pas dans le tableau.
    """
    if cible not in df.columns:
        raise ValueError(f"La colonne {cible} est introuvable")
    X = pd.get_dummies(df.drop(columns=[cible]), drop_first=True, dtype=float)
    y = df[cible]
    return X, y


def ajouter_constante(X: pd.DataFrame) -> np.ndarray:
    """Ajoute une colonne de 1 devant X, pour l'ordonnée à l'origine.

    Reçoit : le tableau X (n lignes, p colonnes).
    Retourne : un tableau NumPy de n lignes et p + 1 colonnes.
    """
    return np.column_stack([np.ones(len(X)), X.to_numpy(dtype=float)])


def coefficients_a_la_main(X: pd.DataFrame, y: pd.Series) -> np.ndarray:
    """Calcule les coefficients de la régression linéaire par les moindres carrés.

    Reçoit : X, les caractéristiques, et y, les prix.
    Retourne : beta, où beta[0] est l'ordonnée à l'origine et beta[1:]
    les coefficients des colonnes de X, dans le même ordre.
    Lève ValueError si X et y n'ont pas le même nombre de lignes.
    """
    if len(X) != len(y):
        raise ValueError("X et y doivent avoir le même nombre de lignes")
    A = ajouter_constante(X)
    beta, _, _, _ = np.linalg.lstsq(A, y.to_numpy(dtype=float), rcond=None)
    return beta


def predire_lineaire(beta: np.ndarray, X: pd.DataFrame) -> np.ndarray:
    """Prédit les prix avec les coefficients trouvés à la main.

    Reçoit : beta (retourné par coefficients_a_la_main) et X.
    Retourne : un tableau NumPy des prix prédits.
    """
    return ajouter_constante(X) @ beta
