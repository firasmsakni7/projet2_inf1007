from src.donnees import charger_donnees, construire_variables, nettoyer_donnees
from src.interface import Application

if __name__ == "__main__":
    df = nettoyer_donnees(charger_donnees("donnees/car_details_v3.csv"))
    Application(construire_variables(df), df["selling_price"]).lancer()