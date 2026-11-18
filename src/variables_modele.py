"""Construit les champs de l'interface à partir des métadonnées sauvegardées."""
from typing import Any

from src.donnees import Variable, VariableCategorielle, VariableNumerique


def construire_variables_metadonnees(metadonnees: dict[str, Any]) -> list[Variable]:
    """Construit les objets Variable dans l'ordre du modèle.

    Reçoit : les métadonnées JSON d'un modèle déjà entraîné.
    Retourne : la liste des champs numériques ou catégoriels.
    Lève ValueError ou KeyError si les métadonnées sont incomplètes.
    """
    if not isinstance(metadonnees, dict):
        raise ValueError("Les métadonnées doivent être un dictionnaire.")

    resultat: list[Variable] = []
    try:
        for nom in metadonnees["colonnes_entree"]:
            description = metadonnees["variables"][nom]
            if description["type"] == "numerique":
                resultat.append(
                    VariableNumerique(nom, description["minimum"], description["maximum"])
                )
            elif description["type"] == "categorielle":
                resultat.append(VariableCategorielle(nom, description["valeurs"]))
            else:
                raise ValueError(f"Type inconnu pour {nom} : {description['type']}")
    except (KeyError, TypeError) as erreur:
        raise ValueError("Les métadonnées du modèle sont incomplètes.") from erreur
    if not resultat:
        raise ValueError("Le modèle ne définit aucune variable d'entrée.")
    return resultat
