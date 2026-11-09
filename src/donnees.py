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

