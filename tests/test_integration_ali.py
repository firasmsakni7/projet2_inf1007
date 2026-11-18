"""Tests du raccordement de l'interface, sans ouvrir Tkinter (CI sans écran)."""
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from src.donnees import VariableCategorielle, VariableNumerique
from src.exceptions import DonneeInvalideError
from src.interface import Application
from src.variables_modele import construire_variables_metadonnees


@pytest.fixture
def metadonnees_minimales():
    return {
        "colonnes_entree": ["year", "fuel"],
        "variables": {
            "year": {"type": "numerique", "minimum": 2000, "maximum": 2020},
            "fuel": {"type": "categorielle", "valeurs": ["Diesel", "Petrol"]},
        },
    }


def test_champs_suivent_les_metadonnees(metadonnees_minimales):
    champs = construire_variables_metadonnees(metadonnees_minimales)
    assert [var.nom for var in champs] == ["year", "fuel"]
    assert isinstance(champs[0], VariableNumerique)
    assert isinstance(champs[1], VariableCategorielle)
    assert champs[0].valider("2010") == pytest.approx(2010)
    assert champs[1].valider("Diesel") == "Diesel"


def test_metadonnees_incompletes():
    with pytest.raises(ValueError, match="incomplètes"):
        construire_variables_metadonnees({"colonnes_entree": ["year"]})


def test_metadonnees_type_inconnu(metadonnees_minimales):
    metadonnees_minimales["variables"]["fuel"]["type"] = "mystere"
    with pytest.raises(ValueError, match="Type inconnu"):
        construire_variables_metadonnees(metadonnees_minimales)


def test_predire_appelle_modele_et_historise(monkeypatch):
    import src.interface as interface

    saisies = {"year": 2014.0, "fuel": "Diesel"}
    modele = SimpleNamespace(predire=Mock(return_value=320_500.0))
    application = Application.__new__(Application)
    application._modele = modele
    application._resultat = SimpleNamespace(config=Mock())
    application._dessiner_graphique = Mock()
    application._lire_saisies = Mock(return_value=saisies)
    journal = Mock()
    monkeypatch.setattr(interface, "ajouter_historique", journal)
    erreur = Mock()
    monkeypatch.setattr(interface.messagebox, "showerror", erreur)

    application._predire()

    modele.predire.assert_called_once_with(saisies)
    journal.assert_called_once_with(interface.CHEMIN_HISTORIQUE, saisies, 320_500.0)
    application._dessiner_graphique.assert_called_once_with(320_500.0)
    assert "320,500" in application._resultat.config.call_args.kwargs["text"]
    erreur.assert_not_called()


def test_saisie_invalide_ne_sauvegarde_pas(monkeypatch):
    import src.interface as interface

    application = Application.__new__(Application)
    application._modele = SimpleNamespace(predire=Mock())
    application._lire_saisies = Mock(side_effect=DonneeInvalideError("year invalide"))
    application._resultat = SimpleNamespace(config=Mock())
    application._dessiner_graphique = Mock()
    journal = Mock()
    monkeypatch.setattr(interface, "ajouter_historique", journal)
    erreur = Mock()
    monkeypatch.setattr(interface.messagebox, "showerror", erreur)

    application._predire()

    erreur.assert_called_once()
    application._modele.predire.assert_not_called()
    journal.assert_not_called()
    application._resultat.config.assert_not_called()


def test_rejet_du_modele_ne_sauvegarde_pas(monkeypatch):
    import src.interface as interface

    application = Application.__new__(Application)
    application._modele = SimpleNamespace(predire=Mock(side_effect=ValueError("nan interdit")))
    application._lire_saisies = Mock(return_value={"year": float("nan")})
    application._resultat = SimpleNamespace(config=Mock())
    application._dessiner_graphique = Mock()
    journal = Mock()
    monkeypatch.setattr(interface, "ajouter_historique", journal)
    erreur = Mock()
    monkeypatch.setattr(interface.messagebox, "showerror", erreur)

    application._predire()

    erreur.assert_called_once()
    journal.assert_not_called()
    application._resultat.config.assert_not_called()


def test_enregistrement_impossible_affiche_avertissement(monkeypatch):
    import src.interface as interface

    application = Application.__new__(Application)
    application._modele = SimpleNamespace(predire=Mock(return_value=120_000))
    application._lire_saisies = Mock(return_value={"fuel": "Petrol"})
    application._resultat = SimpleNamespace(config=Mock())
    application._dessiner_graphique = Mock()
    monkeypatch.setattr(interface, "ajouter_historique", Mock(side_effect=OSError("disque plein")))
    avertissement = Mock()
    monkeypatch.setattr(interface.messagebox, "showwarning", avertissement)

    application._predire()

    avertissement.assert_called_once()
    application._resultat.config.assert_called_once()
