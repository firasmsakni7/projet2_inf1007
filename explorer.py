import pandas as pd

df = pd.read_csv("donnees/car_details_v3.csv")
df.info()
print(df.head())
print(df.isna().sum())        # valeurs manquantes par colonne
print(df.duplicated().sum())  # lignes en double