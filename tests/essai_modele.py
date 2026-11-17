
from src.donnees import charger_donnees, nettoyer_donnees
from src.modele import (
    separer_donnees,
    modele_reference,
    entrainer_modele,
    rmse_numpy
)

# 1. Charger et nettoyer les donnees
df = charger_donnees("donnees/car_details_v3.csv")
df = nettoyer_donnees(df)

# 2. Separer les donnees
X_train, X_test, y_train, y_test = separer_donnees(df)

# 3. Calculer la reference
rmse_base = modele_reference(y_train, y_test)

# 4. Entrainer la foret aleatoire
modele = entrainer_modele(X_train, y_train)

# 5. Predire les prix du test
predictions = modele.predict(X_test)

# 6. Calculer la RMSE du modele
rmse_foret = rmse_numpy(y_test.to_numpy(), predictions)

print(f"RMSE de reference : {rmse_base:.2f} INR")
print(f"RMSE foret aleatoire : {rmse_foret:.2f} INR")
