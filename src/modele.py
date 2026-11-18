"""Entrainement, evaluation et prediction du prix de voitures d'occasion.

Ce module attend un DataFrame nettoye selon le contrat d'integration.
La variable cible est le prix en roupies indiennes (INR).
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from functools import wraps
import json
import os
from time import perf_counter
from typing import Any, TypeVar

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


F = TypeVar("F", bound=Callable[..., Any])
CIBLE = "selling_price"
COLONNES_NUMERIQUES = ("year", "km_driven", "engine", "max_power")
COLONNES_CATEGORIELLES = ("fuel", "seller_type", "transmission", "owner", "marque")
COLONNES_ENTREE = COLONNES_NUMERIQUES + COLONNES_CATEGORIELLES
GRAINE = 42


def chronometrer(fonction: F) -> F:
    """Affiche le temps d'execution d'une fonction sans modifier son resultat.

    Parametres : fonction callable a decorer.
    Retour : fonction decoree avec la meme signature pratique.
    Echec : propage toute exception de la fonction originale.
    """

    @wraps(fonction)
    def enveloppe(*args: Any, **kwargs: Any) -> Any:
        debut = perf_counter()
        try:
            return fonction(*args, **kwargs)
        finally:
            duree = perf_counter() - debut
            print(f"{fonction.__name__} : {duree:.3f} s")

    return enveloppe  # type: ignore[return-value]


def rmse_numpy(reels: Sequence[float], predictions: Sequence[float]) -> float:
    """Calcule la RMSE vectorisee avec NumPy (aucune boucle Python).

    Parametres : deux sequences numeriques de meme taille et non vides.
    Retour : racine de la moyenne des erreurs au carre.
    Echec : ValueError si dimensions, taille ou valeurs invalides.
    """
    y_reel = np.asarray(reels, dtype=float)
    y_predit = np.asarray(predictions, dtype=float)
    if y_reel.ndim != 1 or y_predit.ndim != 1:
        raise ValueError("Les valeurs doivent etre des vecteurs a une dimension.")
    if y_reel.size == 0 or y_reel.shape != y_predit.shape:
        raise ValueError("Les tableaux doivent etre non vides et de meme longueur.")
    if not np.isfinite(y_reel).all() or not np.isfinite(y_predit).all():
        raise ValueError("Les tableaux ne peuvent contenir NaN ou l'infini.")
    return float(np.sqrt(np.mean((y_reel - y_predit) ** 2)))


class ModelePrixVoiture:
    """Contient un pipeline d'estimation et ses metadonnees (encapsulation)."""

    def __init__(self) -> None:
        """Initialise un modele non entraine.

        Parametres : aucun. Retour : aucun. Echec : aucun.
        """
        self._pipeline: Pipeline | None = None
        self._metadonnees: dict[str, Any] = {}

    @property
    def metadonnees(self) -> dict[str, Any]:
        """Renvoie une copie superficielle des metadonnees disponibles."""
        return self._metadonnees.copy()

    @staticmethod
    def _creer_pipeline() -> Pipeline:
        """Cree le pretraitement des donnees et une foret aleatoire."""
        pretraitement = ColumnTransformer(
            transformers=[
                (
                    "numeriques",
                    Pipeline([("valeurs_manquantes", SimpleImputer(strategy="median"))]),
                    list(COLONNES_NUMERIQUES),
                ),
                (
                    "categories",
                    Pipeline(
                        [
                            ("valeurs_manquantes", SimpleImputer(strategy="most_frequent")),
                            ("encodage", OneHotEncoder(handle_unknown="ignore")),
                        ]
                    ),
                    list(COLONNES_CATEGORIELLES),
                ),
            ]
        )
        return Pipeline(
            [
                ("preparation", pretraitement),
                ("regression", RandomForestRegressor(
                    n_estimators=100,
                    max_depth=10,
                    min_samples_leaf=3,
                    random_state=GRAINE,
                    n_jobs=-1,
                )),
            ]
        )

    @staticmethod
    def _preparer_entrees(donnees: pd.DataFrame) -> pd.DataFrame:
        """Copie les variables d'entree et convertit les colonnes numeriques.

        Parametres : donnees avec les neuf colonnes requises.
        Retour : DataFrame compatible avec le pipeline.
        Echec : KeyError si une colonne est absente.
        """
        x = donnees.loc[:, list(COLONNES_ENTREE)].copy()
        for nom in COLONNES_NUMERIQUES:
            x[nom] = pd.to_numeric(x[nom], errors="coerce")
        for nom in COLONNES_CATEGORIELLES:
            x[nom] = x[nom].astype(object).where(x[nom].notna(), np.nan)
        return x

    @chronometrer
    def entrainer(self, donnees: pd.DataFrame) -> dict[str, Any]:
        """Separe, entraine, compare a la moyenne et conserve les metriques.

        Parametres : DataFrame contenant les neuf entrees et selling_price.
        Retour : copie des metadonnees, dont RMSE et R2 sur le jeu test.
        Echec : ValueError si les donnees ne peuvent etre utilisees.

        Ne pas executer sur le jeu officiel avant validation C par l'auxiliaire.
        """
        requises = set(COLONNES_ENTREE) | {CIBLE}
        absentes = sorted(requises - set(donnees.columns))
        if absentes:
            raise ValueError(f"Colonnes manquantes : {', '.join(absentes)}")

        x = self._preparer_entrees(donnees)
        y = pd.to_numeric(donnees[CIBLE], errors="coerce")
        corrects = np.isfinite(y.to_numpy(dtype=float)) & (y.to_numpy(dtype=float) > 0)
        x, y = x.loc[corrects], y.loc[corrects]
        if len(x) < 30:
            raise ValueError("Au moins 30 observations avec un prix valide sont necessaires.")

        x_entrainement, x_test, y_entrainement, y_test = train_test_split(
            x, y, test_size=0.20, random_state=GRAINE
        )

        # Le pretraitement (y compris les imputations) est ajuste sur le train UNIQUEMENT.
        modele = self._creer_pipeline()
        modele.fit(x_entrainement, y_entrainement)
        predictions = modele.predict(x_test)

        reference = DummyRegressor(strategy="mean")
        reference.fit(x_entrainement, y_entrainement)
        predictions_reference = reference.predict(x_test)

        # Les bornes et categories proviennent uniquement du jeu d'entrainement.
        variables: dict[str, dict[str, Any]] = {}
        for nom in COLONNES_NUMERIQUES:
            valeurs = x_entrainement[nom].dropna()
            if valeurs.empty:
                raise ValueError(f"La variable {nom} ne contient aucune valeur numerique.")
            variables[nom] = {
                "type": "numerique",
                "minimum": float(valeurs.min()),
                "maximum": float(valeurs.max()),
            }
        for nom in COLONNES_CATEGORIELLES:
            categories = sorted(str(v) for v in x_entrainement[nom].dropna().unique())
            if not categories:
                raise ValueError(f"La variable {nom} ne contient aucune categorie.")
            variables[nom] = {"type": "categorielle", "valeurs": categories}

        effectifs, bornes = np.histogram(y_entrainement.to_numpy(dtype=float), bins=20)
        self._pipeline = modele
        self._metadonnees = {
            "cible": CIBLE,
            "unite": "INR",
            "colonnes_entree": list(COLONNES_ENTREE),
            "variables": variables,
            "metriques": {
                "rmse": rmse_numpy(y_test, predictions),
                "rmse_reference": rmse_numpy(y_test, predictions_reference),
                "r2": float(r2_score(y_test, predictions)),
                "nombre_entrainement": int(len(x_entrainement)),
                "nombre_test": int(len(x_test)),
                "graine": GRAINE,
            },
            "distribution": {
                "bornes": bornes.tolist(),
                "effectifs": effectifs.astype(int).tolist(),
            },
        }
        return self.metadonnees

    def predire(self, caracteristiques: Mapping[str, Any]) -> float:
        """Estime le prix d'une voiture en INR apres verification des entrees.

        Parametres : dictionnaire des neuf valeurs saisies.
        Retour : prix estime (float) en INR.
        Echec : RuntimeError si modele absent, ValueError si entree invalide.
        """
        if self._pipeline is None or not self._metadonnees:
            raise RuntimeError("Le modele doit etre entraine ou charge avant de predire.")
        valeurs: dict[str, Any] = {}
        for nom in COLONNES_ENTREE:
            if nom not in caracteristiques or caracteristiques[nom] is None:
                raise ValueError(f"Veuillez renseigner : {nom}.")
            infos = self._metadonnees["variables"][nom]
            valeur = caracteristiques[nom]
            if infos["type"] == "numerique":
                if isinstance(valeur, str) and not valeur.strip():
                    raise ValueError(f"Veuillez renseigner : {nom}.")
                try:
                    nombre = float(valeur)
                except (TypeError, ValueError) as erreur:
                    raise ValueError(f"{nom} doit etre numerique.") from erreur
                if not np.isfinite(nombre):
                    raise ValueError(f"{nom} doit etre fini.")
                if not infos["minimum"] <= nombre <= infos["maximum"]:
                    raise ValueError(
                        f"{nom} doit etre entre {infos['minimum']:g} et {infos['maximum']:g}."
                    )
                valeurs[nom] = nombre
            else:
                if not isinstance(valeur, str) or valeur not in infos["valeurs"]:
                    raise ValueError(f"Valeur invalide pour {nom} : {valeur!r}.")
                valeurs[nom] = valeur
        entree = pd.DataFrame([valeurs], columns=list(COLONNES_ENTREE))
        return float(self._pipeline.predict(entree)[0])

    def sauvegarder(self, dossier: str) -> None:
        """Enregistre un modele joblib et ses metadonnees JSON.

        Parametres : chemin vers le dossier de sortie.
        Retour : aucun. Echec : RuntimeError si modele absent, OSError sinon.
        """
        if self._pipeline is None or not self._metadonnees:
            raise RuntimeError("Aucun modele entraine a sauvegarder.")
        os.makedirs(dossier, exist_ok=True)
        chemin_modele = os.path.join(dossier, "prix_voiture.joblib")
        chemin_meta = os.path.join(dossier, "metadonnees.json")
        with open(chemin_modele, "wb") as fichier:
            joblib.dump(self._pipeline, fichier)
        with open(chemin_meta, "w", encoding="utf-8") as fichier:
            json.dump(self._metadonnees, fichier, indent=2, ensure_ascii=False)

    @classmethod
    def charger(cls, dossier: str) -> "ModelePrixVoiture":
        """Charge les fichiers sauvegardes, sans reentrainer.

        Parametres : dossier contenant prix_voiture.joblib et metadonnees.json.
        Retour : instance prete a predire.
        Echec : FileNotFoundError si fichier absent, erreurs joblib/JSON sinon.
        Attention : ouvrir seulement vos propres fichiers joblib de confiance.
        """
        chemin_modele = os.path.join(dossier, "prix_voiture.joblib")
        chemin_meta = os.path.join(dossier, "metadonnees.json")
        for chemin in (chemin_modele, chemin_meta):
            if not os.path.isfile(chemin):
                raise FileNotFoundError(f"Fichier introuvable : {chemin}")
        instance = cls()
        with open(chemin_modele, "rb") as fichier:
            instance._pipeline = joblib.load(fichier)
        with open(chemin_meta, "r", encoding="utf-8") as fichier:
            instance._metadonnees = json.load(fichier)
        return instance

    def __str__(self) -> str:
        """Decrit le modele avec son statut d'entrainement."""
        statut = "entraine" if self._pipeline is not None else "non entraine"
        return f"ModelePrixVoiture ({statut})"


def separer_donnees(
    df: pd.DataFrame, cible: str = CIBLE
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Separe un DataFrame en 80 % d'entrainement et 20 % de test.

    Recoit : un DataFrame et le nom de la cible.
    Retourne : X_train, X_test, y_train, y_test.
    Echec : ValueError si le jeu de donnees est vide ou sans cible.
    """
    if df.empty:
        raise ValueError("Le jeu de donnees est vide.")
    if cible not in df.columns:
        raise ValueError(f"La colonne cible {cible} est introuvable.")
    x = df.drop(columns=[cible])
    y = df[cible]
    return train_test_split(x, y, test_size=0.20, random_state=GRAINE)


def modele_reference(y_train: pd.Series, y_test: pd.Series) -> float:
    """Calcule la RMSE d'une reference qui predit le prix moyen du train.

    Recoit : prix d'entrainement et prix de test.
    Retourne : RMSE de la reference.
    Echec : ValueError si une des series est vide.
    """
    if len(y_train) == 0 or len(y_test) == 0:
        raise ValueError("Les series de prix ne doivent pas etre vides.")
    predictions = np.full(len(y_test), float(np.mean(y_train)))
    return rmse_numpy(y_test, predictions)


def entrainer_modele(X_train: pd.DataFrame, y_train: pd.Series) -> Pipeline:
    """Entraine le pipeline sur les caracteristiques fournies.

    Recoit : DataFrame X_train avec les 9 caracteristiques, Series y_train.
    Retourne : pipeline scikit-learn entraine.
    Echec : ValueError si les donnees sont vides ou incompatibles.
    """
    if X_train.empty or len(y_train) == 0 or len(X_train) != len(y_train):
        raise ValueError("Donnees d'entrainement vides ou incompatibles.")
    x = ModelePrixVoiture._preparer_entrees(X_train)
    modele = ModelePrixVoiture._creer_pipeline()
    modele.fit(x, y_train)
    return modele
