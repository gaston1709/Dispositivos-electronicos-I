import pandas as pd

# valores fijos de IG
IG_values = [10, 20, 30, 40, 50]

# inicializo listas vacías
Vcc_list = []
IAK_list = []
VAK_list = []

# pido datos al usuario
for ig in IG_values:
    print(f"\nIG = {ig} µA")
    Vcc = float(input("Vcc [V]: "))
    IAK = float(input("IAK [mA]: "))
    VAK = float(input("VAK [V]: "))
    
    Vcc_list.append(Vcc)
    IAK_list.append(IAK)
    VAK_list.append(VAK)

# armo dataframe
df = pd.DataFrame({
    "IG [µA]": IG_values,
    "Vcc [V]": Vcc_list,
    "IAK [mA]": IAK_list,
    "VAK [V]": VAK_list
})

# muestro en consola
print("\nTabla final:\n")
print(df.to_string(index=False))

# opcional: guardar en CSV
df.to_csv("mediciones_scr.csv", index=False)
print("\nDatos guardados en mediciones_scr.csv")

