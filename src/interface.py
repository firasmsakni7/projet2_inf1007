import tkinter as tk
from tkinter import ttk

from src.donnees import Variable, VariableCategorielle
from tkinter import messagebox

from src.exceptions import DonneeInvalideError

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
        tk.Button(self._fenetre, text="Prédire", command=self._predire).pack(pady=10)
        self._resultat = tk.Label(self._fenetre, text="", font=("Arial", 14))
        self._resultat.pack(pady=10)


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
    
    
    def _lire_saisies(self) -> dict:
        """Lit et valide chaque champ. Lève DonneeInvalideError si une saisie est invalide."""
        saisies = {}
        for variable in self._variables:
            texte = self._champs[variable.nom].get().strip()
            saisies[variable.nom] = variable.valider(texte)   # polymorphisme
        return saisies


    def _predire(self) -> None:
        """Appelée par le bouton : valide les saisies et affiche le résultat."""
        try:
            saisies = self._lire_saisies()
        except DonneeInvalideError as erreur:
            messagebox.showerror("Saisie invalide", str(erreur))
            return
        self._resultat.config(text="Saisies valides")