import pytest
from src.donnees import charger_donnees
from src.donnees import extraire_nombre , nettoyer_donnees
import pandas as pd


def test_charger_donnees_vrai_fichier():
    df = charger_donnees("donnees/car_details_v3.csv")
    assert len(df) == 8128


def test_charger_donnees_fichier_absent():
    with pytest.raises(FileNotFoundError):
        charger_donnees("donnees/absent.csv")


def test_extraire_nombre_usuel_et_limite():
    colonne = pd.Series(["1248 CC", " bhp"])
    resultat = extraire_nombre(colonne)
    assert resultat[0] == 1248.0
    assert pd.isna(resultat[1])


def test_nettoyer_donnees():
    df = nettoyer_donnees(charger_donnees("donnees/car_details_v3.csv"))
    assert df.duplicated().sum() == 0
    assert df.isna().sum().sum() == 0
    assert "torque" not in df.columns
    assert "name" not in df.columns
    assert "marque" in df.columns