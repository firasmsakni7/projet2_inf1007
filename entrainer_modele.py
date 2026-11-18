"""Entraînement hors interface, à exécuter après la validation C.

Depuis la racine : python entrainer_modele.py --validation-c
"""
import argparse
import os

from src.donnees import charger_donnees, nettoyer_donnees
from src.modele import ModelePrixVoiture

RACINE = os.path.dirname(os.path.abspath(__file__))


def main() -> None:
    """Charge les voitures, entraîne une seule fois et sauvegarde le modèle."""
    analyseur = argparse.ArgumentParser(description="Entraîner le modèle CarDekho")
    analyseur.add_argument(
        "--validation-c", action="store_true",
        help="Confirme que les choix ont été présentés à l'auxiliaire (validation C).",
    )
    arguments = analyseur.parse_args()
    if not arguments.validation_c:
        analyseur.error(
            "Validation C à effectuer avant l'entraînement officiel. "
            "Relancer avec --validation-c une fois celle-ci obtenue."
        )
    chemin_csv = os.path.join(RACINE, "donnees", "car_details_v3.csv")
    donnees = nettoyer_donnees(charger_donnees(chemin_csv))
    modele = ModelePrixVoiture()
    metadonnees = modele.entrainer(donnees)
    dossier = os.path.join(RACINE, "modeles")
    modele.sauvegarder(dossier)
    valeurs = metadonnees["metriques"]
    print(f"Données nettoyées : {len(donnees)} observations")
    print(f"Entraînement : {valeurs['nombre_entrainement']} observations")
    print(f"Test : {valeurs['nombre_test']} observations")
    print(f"RMSE référence : {valeurs['rmse_reference']:,.2f} INR")
    print(f"RMSE forêt aléatoire : {valeurs['rmse']:,.2f} INR")
    print(f"R² : {valeurs['r2']:.3f}")
    print(f"Modèle enregistré dans {dossier}")


if __name__ == "__main__":
    main()
