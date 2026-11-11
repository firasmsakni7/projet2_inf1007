from src.donnees import charger_donnees, nettoyer_donnees, tracer_exploration

df = nettoyer_donnees(charger_donnees("donnees/car_details_v3.csv"))
tracer_exploration(df, "figures/prix_selon_annee.png")