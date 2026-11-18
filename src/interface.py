import tkinter as tk
from tkinter import ttk

from src.donnees import Variable, VariableCategorielle


class Application:
    """Fenêtre principale : estime le prix d'une voiture d'occasion."""

    def __init__(self, variables: list[Variable]) -> None:
        self._variables = variables          # composition : l'application contient les variables
        self._champs = {}                    # nom de la variable -> champ de saisie
        self._fenetre = tk.Tk()
        self._fenetre.title("Prix d'une voiture d'occasion")
        tk.Label(self._fenetre, text="Estimez le prix de votre voiture",
                 font=("Arial", 16)).pack(pady=10)
        self._creer_champs()

    def _creer_champs(self) -> None:
        """Crée une ligne (étiquette + champ) par variable."""
        cadre = tk.Frame(self._fenetre)
        cadre.pack(padx=20, pady=10)
        for ligne, variable in enumerate(self._variables):
            tk.Label(cadre, text=variable.nom).grid(row=ligne, column=0, sticky="w", pady=2)
            if isinstance(variable, VariableCategorielle):
                champ = ttk.Combobox(cadre, values=variable.valeurs, state="readonly")
            else:
                champ = tk.Entry(cadre)
            champ.grid(row=ligne, column=1, pady=2)
            self._champs[variable.nom] = champ

    def lancer(self) -> None:
        """Affiche la fenêtre et attend les actions de l'utilisateur."""
        self._fenetre.mainloop()