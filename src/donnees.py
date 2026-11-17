import os
import pandas as pd
import matplotlib.pyplot as plt

def charger_donnees(chemin: str) -> pd.DataFrame:
    """Charge le jeu de données CSV des voitures d'occasion.

    Reçoit : chemin, le chemin du fichier CSV.
    Retourne : un DataFrame pandas avec une ligne par voiture.
    Lève FileNotFoundError si le fichier n'existe pas.
    """
    if not os.path.exists(chemin):
        raise FileNotFoundError(f"Le fichier {chemin} n'existe pas")
    return pd.read_csv(chemin)

def extraire_nombre(colonne: pd.Series) -> pd.Series:
    """Convertit une colonne de texte avec unité en colonne de nombres.
    Reçoit : une colonne de textes comme "1248 CC" ou "74 bhp".
    Retourne : une colonne de nombres (1248.0, 74.0).
    Cas limite : une valeur sans nombre (ex. " bhp") devient manquante (NaN).
    """
    premier_mot = colonne.str.split(" ").str[0]
    return pd.to_numeric(premier_mot, errors="coerce")

def nettoyer_donnees(df: pd.DataFrame) -> pd.DataFrame:
    """Nettoie le jeu de données des voitures d'occasion.

    Reçoit : le tableau brut retourné par charger_donnees.
    Retourne : un tableau sans doublons ni valeurs manquantes, où
    mileage, engine et max_power sont des nombres et où la colonne
    name est remplacée par la marque.
    """
    df = df.drop(columns=["torque"])
    df = df.dropna()
    for nom in ["mileage", "engine", "max_power"]:
        df[nom] = extraire_nombre(df[nom])
    df = df.dropna()
    df["marque"] = df["name"].str.split(" ").str[0]
    df = df.drop(columns=["name"])
    df = df.drop_duplicates()

    return df

def tracer_exploration(df: pd.DataFrame, chemin_image: str) -> None:
    """Enregistre un nuage de points du prix de vente selon l'année.

    Reçoit : df, le tableau nettoyé, et chemin_image, le fichier PNG à créer.
    Ne retourne rien : l'image est enregistrée à l'emplacement chemin_image.
    """
    plt.figure()
    plt.scatter(df["year"], df["selling_price"], alpha=0.3)
    plt.title("Prix de vente des voitures d'occasion selon l'année")
    plt.xlabel("Année")
    plt.ylabel("Prix de vente (roupies)")
    plt.savefig(chemin_image)
    plt.close()

from src.exceptions import DonneeInvalideError


class Variable:
    """Variable d'entrée du modèle, identifiée par son nom.

    Classe parente de VariableNumerique et VariableCategorielle.
    """

    def __init__(self, nom: str) -> None:
        self._nom = nom

    @property
    def nom(self) -> str:
        """Retourne le nom de la variable (lecture seule)."""
        return self._nom

    def valider(self, saisie: str):
        """Vérifie une saisie de l'utilisateur.

        Redéfinie par chaque classe enfant.
        Lève NotImplementedError si elle est appelée sur Variable.
        """
        raise NotImplementedError("à redéfinir")


class VariableNumerique(Variable):
    """Variable numérique dont la valeur doit être dans un intervalle."""

    def __init__(self, nom: str, minimum: float, maximum: float) -> None:
        super().__init__(nom)
        self._minimum = minimum
        self._maximum = maximum

    def valider(self, saisie: str) -> float:
        """Convertit la saisie en nombre et vérifie l'intervalle.

        Reçoit : le texte tapé par l'utilisateur (ex. "2015").
        Retourne : le nombre (ex. 2015.0).
        Lève DonneeInvalideError si la saisie est vide, n'est pas
        un nombre, ou est hors de l'intervalle.
        """
        try:
            nombre = float(saisie)
        except ValueError:
            raise DonneeInvalideError(f"{self.nom} : la valeur doit être un nombre")
        if nombre < self._minimum or nombre > self._maximum:
            raise DonneeInvalideError(
                f"{self.nom} : la valeur doit être entre {self._minimum} et {self._maximum}"
            )
        return nombre
    
class VariableCategorielle(Variable):
    """Variable catégorielle : la saisie doit faire partie d'une liste de valeurs permises."""

    def __init__(self, nom: str, valeurs: list[str]) -> None:
        super().__init__(nom)
        self._valeurs = valeurs

    def valider(self, saisie: str) -> str:
        """Vérifie que la saisie est une valeur permise.

        Reçoit : le texte choisi par l'utilisateur (ex. "Diesel").
        Retourne : la saisie, si elle est permise.
        Lève DonneeInvalideError si la saisie n'est pas dans la liste.
        """
        if saisie not in self._valeurs:
            raise DonneeInvalideError(f"{self.nom} : choisir parmi {self._valeurs}")
        return saisie