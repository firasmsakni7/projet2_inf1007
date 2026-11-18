"""Point d'entrée de l'application (à lancer depuis la racine du dépôt)."""
import os
import tkinter as tk
from tkinter import messagebox

from src.donnees import charger_donnees, nettoyer_donnees
from src.interface import Application
from src.modele import ModelePrixVoiture
from src.variables_modele import construire_variables_metadonnees

RACINE = os.path.dirname(os.path.abspath(__file__))


def main() -> None:
    """Charge le modèle déjà enregistré, puis affiche l'interface sans l'entraîner."""
    try:
        modele = ModelePrixVoiture.charger(os.path.join(RACINE, "modeles"))
        variables = construire_variables_metadonnees(modele.metadonnees)
        chemin_csv = os.path.join(RACINE, "donnees", "car_details_v3.csv")
        donnees = nettoyer_donnees(charger_donnees(chemin_csv))
    except (FileNotFoundError, OSError, ValueError, KeyError) as erreur:
        fenetre = tk.Tk()
        fenetre.withdraw()
        messagebox.showerror(
            "Démarrage impossible",
            f"{erreur}\n\nVérifiez le CSV et les fichiers dans modeles/. "
            "L'entraînement du modèle doit avoir été fait une fois au préalable.",
            parent=fenetre,
        )
        fenetre.destroy()
        return

    application = Application(variables, donnees["selling_price"], modele)
    application.lancer()


if __name__ == "__main__":
    main()
