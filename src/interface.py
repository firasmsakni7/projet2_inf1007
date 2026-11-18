"""Interface Tkinter écrite par Firas, avec le branchement du modèle d'Ali.

Les champs, les validations, l'historique et le graphique viennent de la branche
firas-interface. L'intégration remplace le prix provisoire 0.0 par une véritable
prédiction et construit les champs à partir des métadonnées du modèle.
"""
import os
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from src.donnees import (
    Variable,
    VariableCategorielle,
    ajouter_historique,
    lire_historique,
)
from src.exceptions import DonneeInvalideError
from src.modele import ModelePrixVoiture

RACINE_PROJET = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHEMIN_HISTORIQUE = os.path.join(RACINE_PROJET, "donnees", "historique.csv")
# Taux indicatif au 17 novembre 2026, fixe pour fonctionner sans connexion Internet.
TAUX_INR_USD = 0.0107


class Application:
    """Fenêtre principale : saisit les variables et affiche une estimation."""

    def __init__(
        self,
        variables: list[Variable],
        prix_donnees: Any,
        modele: ModelePrixVoiture,
    ) -> None:
        """Prépare les champs et le graphique à partir d'objets composés."""
        self._variables = variables       # Composition : contient des objets Variable.
        self._modele = modele             # Composition : contient le modèle chargé.
        self._prix_donnees = prix_donnees
        self._champs: dict[str, tk.Widget] = {}
        self._fenetre = tk.Tk()
        self._fenetre.title("Prix d'une voiture d'occasion")
        self._fenetre.geometry("650x790")
        tk.Label(
            self._fenetre,
            text="Estimez le prix de votre voiture",
            font=("Arial", 16),
        ).pack(pady=8)
        tk.Label(
            self._fenetre,
            text="Exercice pédagogique — prix indicatif, pas un conseil d'achat ou de vente.",
            wraplength=610,
            fg="#555555",
        ).pack(pady=2)
        self._creer_champs()
        tk.Button(self._fenetre, text="Prédire", command=self._predire).pack(pady=7)
        self._resultat = tk.Label(
            self._fenetre, text="", font=("Arial", 14), wraplength=610
        )
        self._resultat.pack(pady=7)
        tk.Label(
            self._fenetre,
            text="Conversion indicative au taux fixe du 17/11/2026",
            fg="#555555",
            font=("Arial", 9),
        ).pack(pady=1)
        tk.Button(
            self._fenetre,
            text="Voir l'historique",
            command=self._afficher_historique,
        ).pack(pady=4)
        self._figure = Figure(figsize=(5.6, 2.8), dpi=100)
        self._axes = self._figure.add_subplot()
        self._canvas = FigureCanvasTkAgg(self._figure, master=self._fenetre)
        self._canvas.get_tk_widget().pack(pady=10, fill="both", expand=True)
        self._dessiner_graphique(None)

    def _creer_champs(self) -> None:
        """Crée une étiquette et un champ par variable définie par le modèle."""
        cadre = tk.Frame(self._fenetre)
        cadre.pack(padx=20, pady=10)
        for ligne, variable in enumerate(self._variables):
            tk.Label(cadre, text=variable.nom).grid(
                row=ligne, column=0, sticky="w", pady=2, padx=5
            )
            if isinstance(variable, VariableCategorielle):
                champ = ttk.Combobox(
                    cadre, values=variable.valeurs, state="readonly", width=30
                )
            else:
                champ = tk.Entry(cadre, width=33)
            champ.grid(row=ligne, column=1, pady=2)
            self._champs[variable.nom] = champ

    def _lire_saisies(self) -> dict[str, float | str]:
        """Lit les champs et valide les saisies avec le polymorphisme."""
        saisies: dict[str, float | str] = {}
        for variable in self._variables:
            texte = self._champs[variable.nom].get().strip()
            saisies[variable.nom] = variable.valider(texte)
        return saisies

    def _predire(self) -> None:
        """Prédit, affiche et historise une voiture ; signale toute erreur attendue."""
        try:
            saisies = self._lire_saisies()
            prix = self._modele.predire(saisies)
        except (DonneeInvalideError, ValueError, RuntimeError) as erreur:
            messagebox.showerror("Saisie invalide", str(erreur))
            return

        prix_usd = prix * TAUX_INR_USD
        self._resultat.config(
            text=f"Prix estimé : {prix:,.0f} ₹ (INR) ≈ {prix_usd:,.2f} $ US (USD)"
        )
        self._dessiner_graphique(prix)
        try:
            ajouter_historique(CHEMIN_HISTORIQUE, saisies, prix)
        except OSError as erreur:
            messagebox.showwarning(
                "Historique indisponible",
                f"Prédiction calculée, mais l'historique n'a pas été enregistré : {erreur}",
            )

    def _afficher_historique(self) -> None:
        """Affiche les dix dernières prédictions enregistrées."""
        try:
            lignes = lire_historique(CHEMIN_HISTORIQUE)
        except OSError as erreur:
            messagebox.showerror("Historique indisponible", str(erreur))
            return
        if len(lignes) <= 1:
            messagebox.showinfo("Historique", "Aucune prédiction pour l'instant.")
            return
        texte = ", ".join(lignes[0]) + "\n" + "\n".join(
            ", ".join(ligne) for ligne in lignes[-10:]
        )
        messagebox.showinfo("Historique (10 dernières)", texte)

    def _dessiner_graphique(self, prix: float | None) -> None:
        """Dessine la distribution des prix et la position de la prédiction."""
        self._axes.clear()
        self._axes.hist(self._prix_donnees, bins=50, label="Voitures du dataset")
        if prix is not None:
            self._axes.axvline(prix, color="red", label="Votre voiture")
        self._axes.legend()
        self._axes.set_title("Prix des voitures d'occasion")
        self._axes.set_xlabel("Prix de vente (roupies indiennes)")
        self._axes.set_ylabel("Nombre de voitures")
        self._figure.tight_layout()
        self._canvas.draw()

    def lancer(self) -> None:
        """Ouvre la boucle d'événements Tkinter, jusqu'à fermeture."""
        self._fenetre.mainloop()

    def __str__(self) -> str:
        """Retourne une description brève de l'application."""
        return f"Application ({len(self._variables)} variables, modèle {self._modele})"
