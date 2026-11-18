from src.donnees import charger_donnees, nettoyer_donnees, construire_variables
from src.interface import Application

if __name__ == "__main__":
    df = nettoyer_donnees(charger_donnees("donnees/car_details_v3.csv"))
    Application(construire_variables(df)).lancer()