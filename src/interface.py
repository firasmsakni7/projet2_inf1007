import tkinter as tk
from tkinter import messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from src.donnees import (
    Variable,
    VariableCategorielle,
    ajouter_historique,
    lire_historique,
)
from src.exceptions import DonneeInvalideError

CHEMIN_HISTORIQUE = "donnees/historique.csv"


class Application:
    """Fenêtre principale : estime le prix d'une voiture d'occasion."""

    def __init__(self, variables: list[Variable], prix_donnees) -> None:
        self._variables = variables          # composition : l'application contient les variables
        self._prix_donnees = prix_donnees    # les prix des voitures du jeu de données
        self._champs = {}                    # nom de la variable -> champ de saisie
        self._fenetre = tk.Tk()
        self._fenetre.title("Prix d'une voiture d'occasion")
        tk.Label(self._fenetre, text="Estimez le prix de votre voiture",
                 font=("Arial", 16)).pack(pady=10)
        self._creer_champs()
        tk.Button(self._fenetre, text="Prédire", command=self._predire).pack(pady=10)
        self._resultat = tk.Label(self._fenetre, text="", font=("Arial", 14))
        self._resultat.pack(pady=10)
        tk.Button(self._fenetre, text="Voir l'historique",
                  command=self._afficher_historique).pack(pady=5)
        self._figure = Figure(figsize=(5, 3))
        self._axes = self._figure.add_subplot()
        self._canvas = FigureCanvasTkAgg(self._figure, master=self._fenetre)
        self._canvas.get_tk_widget().pack(pady=10)
        self._dessiner_graphique(None)

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

    def _lire_saisies(self) -> dict:
        """Lit et valide chaque champ. Lève DonneeInvalideError si une saisie est invalide."""
        saisies = {}
        for variable in self._variables:
            texte = self._champs[variable.nom].get().strip()
            saisies[variable.nom] = variable.valider(texte)   # polymorphisme
        return saisies

    def _predire(self) -> None:
        """Appelée par le bouton : valide les saisies, enregistre et affiche le résultat."""
        try:
            saisies = self._lire_saisies()
        except DonneeInvalideError as erreur:
            messagebox.showerror("Saisie invalide", str(erreur))
            return
        prix = 0.0       # TEMPORAIRE : remplacé par la vraie prédiction du modèle d'Ali
        ajouter_historique(CHEMIN_HISTORIQUE, saisies, prix)
        self._resultat.config(text=f"Prix estimé : {prix:,.0f} roupies")
        self._dessiner_graphique(prix)

    def _afficher_historique(self) -> None:
        """Affiche les 10 dernières prédictions dans une petite fenêtre."""
        lignes = lire_historique(CHEMIN_HISTORIQUE)
        if len(lignes) <= 1:
            messagebox.showinfo("Historique", "Aucune prédiction pour l'instant.")
            return
        texte = "\n".join(", ".join(ligne) for ligne in lignes[-10:])
        messagebox.showinfo("Historique", texte)

    def _dessiner_graphique(self, prix) -> None:
        """Dessine la répartition des prix et, si prix est donné, la position de la voiture."""
        self._axes.clear()
        self._axes.hist(self._prix_donnees, bins=50)
        if prix is not None:
            self._axes.axvline(prix, color="red", label="Votre voiture")
            self._axes.legend()
        self._axes.set_title("Position de votre voiture parmi les prix")
        self._axes.set_xlabel("Prix de vente (roupies)")
        self._axes.set_ylabel("Nombre de voitures")
        self._figure.tight_layout()
        self._canvas.draw()

    def lancer(self) -> None:
        """Affiche la fenêtre et attend les actions de l'utilisateur."""
        self._fenetre.mainloop()