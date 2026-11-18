import numpy as np
import pandas as pd
import pytest
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

from src.donnees import charger_donnees, nettoyer_donnees
from src.lineaire import coefficients_a_la_main, predire_lineaire, preparer_matrice


def test_droite_exacte():
    # Les points sont exactement sur la droite y = 1 + 2x.
    X = pd.DataFrame({"x": [0.0, 1.0, 2.0, 3.0]})
    y = pd.Series([1.0, 3.0, 5.0, 7.0])
    beta = coefficients_a_la_main(X, y)
    assert np.allclose(beta, [1.0, 2.0])
    assert np.allclose(predire_lineaire(beta, X), y)


def test_tailles_differentes():
    X = pd.DataFrame({"x": [0.0, 1.0, 2.0]})
    y = pd.Series([1.0, 3.0])
    with pytest.raises(ValueError):
        coefficients_a_la_main(X, y)


def test_cible_absente():
    with pytest.raises(ValueError):
        preparer_matrice(pd.DataFrame({"x": [1, 2]}), "prix")


def test_memes_coefficients_que_scikit_learn():
    df = nettoyer_donnees(charger_donnees("donnees/car_details_v3.csv"))
    X, y = preparer_matrice(df)
    X_train, _, y_train, _ = train_test_split(X, y, test_size=0.2, random_state=42)
    beta = coefficients_a_la_main(X_train, y_train)
    # tol=1e-12 : sinon scikit-learn arrondit à zéro les très petites valeurs singulières
    modele = LinearRegression(tol=1e-12).fit(X_train, y_train)
    assert np.isclose(beta[0], modele.intercept_)
    assert np.allclose(beta[1:], modele.coef_, rtol=1e-6)
