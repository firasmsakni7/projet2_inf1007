import pytest
from src.donnees import charger_donnees


def test_charger_donnees_vrai_fichier():
    df = charger_donnees("donnees/car_details_v3.csv")
    assert len(df) == 8128


def test_charger_donnees_fichier_absent():
    with pytest.raises(FileNotFoundError):
        charger_donnees("donnees/absent.csv")