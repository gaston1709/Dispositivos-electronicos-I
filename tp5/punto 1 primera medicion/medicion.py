# log_vg_ig.py
import argparse
from datetime import datetime
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

def parse_args():
    p = argparse.ArgumentParser(description="Registrar Vg e Ig, guardar a Excel y graficar.")
    p.add_argument("-n", "--num", type=int, required=True, help="Cantidad de muestras a registrar.")
    p.add_argument("-o", "--out", type=str, default="mediciones_Vg_Ig", help="Nombre base de salida (sin extensión).")
    return p.parse_args()

def pedir_float(msg):
    while True:
        try:
            return float(input(msg).replace(",", "."))
        except ValueError:
            print("Valor inválido. Ingresá un número.")

def main():
    args = parse_args()
    registros = []

    print(f"Registrando {args.num} muestras. Ingresá Vg e Ig en cada paso. Ctrl+C para abortar.")
    try:
        for i in range(1, args.num + 1):
            print(f"\nMuestra {i}/{args.num}")
            vg = pedir_float("Vg = ")
            ig = pedir_float("Ig = ")
            t = datetime.now()
            registros.append({"idx": i, "timestamp": t, "Vg": vg, "Ig": ig, "Pg": vg * ig})
    except KeyboardInterrupt:
        print("\nRegistro interrumpido por el usuario.")

    if not registros:
        print("No hay datos. Saliendo.")
        return

    df = pd.DataFrame(registros)
    base = Path(args.out)
    xlsx_path = base.with_suffix(".xlsx")
    csv_path = base.with_suffix(".csv")
    png_path = base.with_suffix(".png")

    # Guardar Excel y CSV
    try:
        df.to_excel(xlsx_path, index=False)
    except Exception as e:
        print(f"No se pudo escribir .xlsx (¿falta openpyxl?). Error: {e}")
    df.to_csv(csv_path, index=False)

    # Graficar
    fig, ax1 = plt.subplots(figsize=(9, 5))
    ax1.plot(df["idx"], df["Vg"], marker="o", label="Vg [V]")
    ax1.set_xlabel("Muestra")
    ax1.set_ylabel("Vg [V]")
    ax1.grid(True, which="both", alpha=0.3)

    ax2 = ax1.twinx()
    ax2.plot(df["idx"], df["Ig"], marker="s", linestyle="--", label="Ig [A]")
    ax2.set_ylabel("Ig [A]")

    # Leyendas combinadas
    lines, labels = [], []
    for ax in (ax1, ax2):
        L = ax.get_lines()
        lines += L
        labels += [l.get_label() for l in L]
    ax1.legend(lines, labels, loc="best")

    plt.title("Registro de Vg e Ig")
    plt.tight_layout()
    plt.savefig(png_path, dpi=150)
    plt.close(fig)

    print(f"Listo.\nCSV:  {csv_path}\nExcel: {xlsx_path}\nGráfico: {png_path}")

if __name__ == "__main__":
    main()

