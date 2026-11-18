"""Tests unitaires de la partie modele (sans interface graphique)."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import mean_squared_error

# Permet pytest depuis la racine sans installer le dossier src comme package.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from modele import ModelePrixVoiture, rmse_numpy  # noqa: E402


@pytest.fixture(scope="module")
def modele_entraine():
    """Cree un petit jeu artificiel et entraine le modele une fois pour les tests."""
    rng = np.random.default_rng(42)
    n = 100
    annees = rng.integers(2005, 2021, n)
    kilometres = rng.integers(3000, 220000, n)
    carburants = rng.choice(["Petrol", "Diesel", "CNG"], n)
    vendeurs = rng.choice(["Individual", "Dealer"], n)
    transmissions = rng.choice(["Automatic", "Manual"], n)
    proprietaires = rng.choice(["First Owner", "Second Owner"], n)
    cylindrees = rng.choice([998, 1197, 1498, 1598, 1968], n)
    puissances = rng.choice([65.0, 78.5, 90.0, 110.0, 150.0], n)
    marques = rng.choice(["Maruti", "Hyundai", "Honda", "Toyota"], n)
    prix = (
        150_000
        + (annees - 2005) * 42_000
        - kilometres * 0.5
        + (transmissions == "Automatic") * 110_000
        + (carburants == "Diesel") * 50_000
        + (cylindrees - 998) * 160
        + puissances * 950
        + rng.normal(0, 25_000, n)
    )
    donnees = pd.DataFrame(
        {
            "year": annees,
            "km_driven": kilometres,
            "engine": cylindrees,
            "max_power": puissances,
            "fuel": carburants,
            "seller_type": vendeurs,
            "transmission": transmissions,
            "owner": proprietaires,
            "marque": marques,
            "selling_price": prix,
        }
    )
    modele = ModelePrixVoiture()
    metadonnees = modele.entrainer(donnees)
    return modele, metadonnees


def _voiture_valide(metadonnees):
    """Construit une saisie situee dans les categories et bornes sauvegardees."""
    valeurs = {}
    for nom, infos in metadonnees["variables"].items():
        if infos["type"] == "numerique":
            valeurs[nom] = (infos["minimum"] + infos["maximum"]) / 2
        else:
            valeurs[nom] = infos["valeurs"][0]
    return valeurs


def test_rmse_numpy_resultat_connu():
    assert rmse_numpy([1, 2, 3], [1, 3, 5]) == pytest.approx(np.sqrt(5 / 3))


def test_rmse_numpy_egale_sklearn():
    vrais, predits = [2, 4, 8, 16], [3, 3, 5, 13]
    assert rmse_numpy(vrais, predits) == pytest.approx(
        np.sqrt(mean_squared_error(vrais, predits))
    )


def test_rmse_numpy_longueurs_differentes():
    with pytest.raises(ValueError):
        rmse_numpy([1, 2], [1])


def test_rmse_numpy_listes_vides():
    with pytest.raises(ValueError):
        rmse_numpy([], [])


def test_rmse_numpy_nan_interdit():
    with pytest.raises(ValueError):
        rmse_numpy([1, float("nan")], [1, 2])


def test_prediction_avant_entrainement_interdite():
    with pytest.raises(RuntimeError):
        ModelePrixVoiture().predire({})


def test_metriques_et_reference(modele_entraine):
    _, meta = modele_entraine
    assert meta["metriques"]["rmse"] >= 0
    assert meta["metriques"]["rmse_reference"] >= 0
    assert meta["metriques"]["nombre_test"] == 20
    assert len(meta["colonnes_entree"]) == 9


def test_prediction_numerique_valide(modele_entraine):
    modele, meta = modele_entraine
    assert modele.predire(_voiture_valide(meta)) > 0


def test_prediction_categorie_invalide(modele_entraine):
    modele, meta = modele_entraine
    valeurs = _voiture_valide(meta)
    valeurs["fuel"] = "Carburant invente"
    with pytest.raises(ValueError):
        modele.predire(valeurs)


def test_prediction_hors_bornes(modele_entraine):
    modele, meta = modele_entraine
    valeurs = _voiture_valide(meta)
    valeurs["year"] = meta["variables"]["year"]["maximum"] + 1
    with pytest.raises(ValueError):
        modele.predire(valeurs)


def test_prediction_non_numerique(modele_entraine):
    modele, meta = modele_entraine
    valeurs = _voiture_valide(meta)
    valeurs["km_driven"] = "beaucoup"
    with pytest.raises(ValueError):
        modele.predire(valeurs)


def test_sauvegarde_et_rechargement(modele_entraine, tmp_path):
    modele, meta = modele_entraine
    saisie = _voiture_valide(meta)
    avant = modele.predire(saisie)
    modele.sauvegarder(str(tmp_path))
    charge = ModelePrixVoiture.charger(str(tmp_path))
    assert charge.predire(saisie) == pytest.approx(avant)
    assert (tmp_path / "metadonnees.json").exists()
    assert (tmp_path / "prix_voiture.joblib").exists()


def test_chargement_dossier_inexistant(tmp_path):
    with pytest.raises(FileNotFoundError):
        ModelePrixVoiture.charger(str(tmp_path))


def test_manque_colonne_requise():
    donnees = pd.DataFrame({"selling_price": [100, 200]})
    with pytest.raises(ValueError, match="Colonnes manquantes"):
        ModelePrixVoiture().entrainer(donnees)


def test_marque_presente_dans_metadonnees(modele_entraine):
    _, meta = modele_entraine
    assert "marque" in meta["variables"]
    assert meta["variables"]["marque"]["type"] == "categorielle"


def test_str_modele(modele_entraine):
    modele, _ = modele_entraine
    assert "entraine" in str(modele)
