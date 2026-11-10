import os
import pandas as pd


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