# gui_mediciones_iak_vcc_vak_fixed.py
import math
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog

import pandas as pd
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

DEFAULT_COLS = ["idx", "timestamp", "Iak[A]", "VCC[V]", "Vak[V]", "P_anodo[W]", "P_fuente[W]"]
NUMERIC_GUESS = {"Iak[A]", "VCC[V]", "Vak[V]", "P_anodo[W]", "P_fuente[W]", "idx"}

def now_ts():
    return datetime.now()

def coerce_float(x):
    if pd.isna(x): return math.nan
    if isinstance(x, (int, float)): return float(x)
    s = str(x).strip().replace(",", ".")
    try: return float(s)
    except: return math.nan

def normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    if "idx" not in df.columns: df.insert(0, "idx", range(1, len(df)+1))
    if "timestamp" not in df.columns: df.insert(1, "timestamp", [now_ts()]*len(df))
    df["idx"] = pd.to_numeric(df["idx"], errors="coerce").fillna(0).astype(int)
    try: df["timestamp"] = pd.to_datetime(df["timestamp"])
    except: df["timestamp"] = [now_ts()]*len(df)
    df = df.sort_values("idx").reset_index(drop=True)
    df["idx"] = range(1, len(df)+1)
    return df

def ensure_default_cols(df: pd.DataFrame) -> pd.DataFrame:
    for c in DEFAULT_COLS:
        if c not in df.columns:
            df[c] = pd.Series([math.nan]*len(df))
    ordered = [c for c in DEFAULT_COLS if c in df.columns]
    rest = [c for c in df.columns if c not in DEFAULT_COLS]
    return df[ordered + rest]

def recalc_powers(df: pd.DataFrame) -> pd.DataFrame:
    if all(c in df.columns for c in ["Vak[V]", "Iak[A]"]):
        df["P_anodo[W]"] = pd.to_numeric(df["Vak[V]"].map(coerce_float)) * pd.to_numeric(df["Iak[A]"].map(coerce_float))
    if all(c in df.columns for c in ["VCC[V]", "Iak[A]"]):
        df["P_fuente[W]"] = pd.to_numeric(df["VCC[V]"].map(coerce_float)) * pd.to_numeric(df["Iak[A]"].map(coerce_float))
    return df

class MedicionesApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mediciones — Editor y Gráficos")
        self.geometry("1200x720")
        self.base_path: Path | None = None
        self.autosave = True  # autosave a CSV si hay ruta conocida
        self.df = ensure_default_cols(normalize_df(pd.DataFrame(columns=DEFAULT_COLS)))
        self._build_ui()
        self._refresh_all()

    # ---------- UI ----------
    def _build_ui(self):
        menubar = tk.Menu(self)
        # Archivo
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Nuevo", command=self.new_file)
        filemenu.add_command(label="Abrir CSV…", command=self.open_csv)
        filemenu.add_separator()
        filemenu.add_command(label="Guardar CSV", command=self.save_csv)
        filemenu.add_command(label="Guardar como CSV…", command=self.save_csv_as)
        filemenu.add_command(label="Exportar Excel", command=self.export_excel)
        filemenu.add_command(label="Exportar PNG", command=self.export_png)
        filemenu.add_separator()
        filemenu.add_checkbutton(label="Autosave", onvalue=True, offvalue=False,
                                 variable=tk.BooleanVar(value=self.autosave),
                                 command=self._toggle_autosave_wrapper)
        filemenu.add_separator()
        filemenu.add_command(label="Salir", command=self.destroy)
        menubar.add_cascade(label="Archivo", menu=filemenu)
        # Editar
        editmenu = tk.Menu(menubar, tearoff=0)
        editmenu.add_command(label="Agregar fila", command=self.add_row)
        editmenu.add_command(label="Borrar fila(s) seleccionada(s)", command=self.del_rows)
        editmenu.add_separator()
        editmenu.add_command(label="Agregar columna…", command=self.add_column)
        editmenu.add_command(label="Borrar columna…", command=self.del_column)
        editmenu.add_separator()
        editmenu.add_command(label="Cambiar N…", command=self.change_n)
        editmenu.add_command(label="Recalcular potencias", command=self.recalc_and_refresh)
        menubar.add_cascade(label="Editar", menu=editmenu)
        self.config(menu=menubar)

        # Layout
        top = ttk.Frame(self); top.pack(fill="both", expand=True)
        # Tabla
        left = ttk.Frame(top); left.pack(side="left", fill="both", expand=True, padx=6, pady=6)
        self.tree = ttk.Treeview(left, show="headings")
        self.tree.bind("<Double-1>", self._edit_cell)
        sy = ttk.Scrollbar(left, orient="vertical", command=self.tree.yview)
        sx = ttk.Scrollbar(left, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        self.tree.pack(side="top", fill="both", expand=True); sy.pack(side="right", fill="y"); sx.pack(side="bottom", fill="x")
        # Botonera
        btnrow = ttk.Frame(left); btnrow.pack(fill="x", pady=4)
        ttk.Button(btnrow, text="Agregar fila", command=self.add_row).pack(side="left")
        ttk.Button(btnrow, text="Borrar fila(s)", command=self.del_rows).pack(side="left", padx=4)
        ttk.Button(btnrow, text="Agregar columna", command=self.add_column).pack(side="left", padx=12)
        ttk.Button(btnrow, text="Borrar columna", command=self.del_column).pack(side="left", padx=4)
        ttk.Button(btnrow, text="Cambiar N", command=self.change_n).pack(side="left", padx=12)
        ttk.Button(btnrow, text="Recalcular potencias", command=self.recalc_and_refresh).pack(side="left", padx=4)

        # Panel derecho
        right = ttk.Frame(top); right.pack(side="left", fill="both", expand=False, padx=6, pady=6)
        sel = ttk.LabelFrame(right, text="Series a graficar"); sel.pack(fill="x")
        ttk.Label(sel, text="X = idx").pack(anchor="w", padx=6, pady=2)
        self.listbox = tk.Listbox(sel, selectmode="multiple", height=10, exportselection=False)
        self.listbox.pack(fill="x", padx=6, pady=4)
        ttk.Button(sel, text="Graficar", command=self._refresh_plot).pack(padx=6, pady=4, fill="x")

        fig = Figure(figsize=(6, 4), dpi=100)
        self.ax1 = fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(fig, master=right)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True, pady=8)

        self.status = tk.StringVar(value="Listo.")
        ttk.Label(self, textvariable=self.status, relief="sunken", anchor="w").pack(fill="x", side="bottom")

    def _toggle_autosave_wrapper(self):
        # Toggle variable leída del menú
        self.autosave = not self.autosave
        self.status.set(f"Autosave: {'ON' if self.autosave else 'OFF'}")

    # ---------- Refresh ----------
    def _refresh_columns(self):
        self.tree["columns"] = list(self.df.columns)
        for c in self.tree["columns"]:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=120, stretch=True)
        self.listbox.delete(0, tk.END)
        for c in self.df.columns:
            if c != "idx":
                self.listbox.insert(tk.END, c)

    def _refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        self._refresh_columns()
        for _, row in self.df.iterrows():
            vals = []
            for c in self.df.columns:
                v = row[c]
                if isinstance(v, pd.Timestamp):
                    v = v.strftime("%Y-%m-%d %H:%M:%S")
                vals.append("" if pd.isna(v) else v)
            self.tree.insert("", tk.END, values=vals)
        self.status.set(self._status_text())

    def _refresh_plot(self):
        self.ax1.clear()
        if "idx" not in self.df.columns or self.df.empty:
            self.canvas.draw(); return
        x = pd.to_numeric(self.df["idx"], errors="coerce")
        sel_idx = self.listbox.curselection()
        if not sel_idx:
            cols_v = [c for c in ["Vak[V]", "VCC[V]"] if c in self.df.columns]
            cols_i = [c for c in ["Iak[A]"] if c in self.df.columns]
        else:
            chosen = [self.listbox.get(i) for i in sel_idx]
            cols_i = [c for c in chosen if "[A]" in c]
            cols_v = [c for c in chosen if c not in cols_i and c != "idx"]
        for c in cols_v:
            y = pd.to_numeric(self.df[c].map(coerce_float), errors="coerce")
            self.ax1.plot(x, y, marker="o", label=c)
        ax2 = None
        if cols_i:
            ax2 = self.ax1.twinx()
            for c in cols_i:
                y = pd.to_numeric(self.df[c].map(coerce_float), errors="coerce")
                ax2.plot(x, y, marker="s", linestyle="--", label=c)
            ax2.set_ylabel("Corriente [A]")
        self.ax1.set_xlabel("idx"); self.ax1.set_ylabel("Magnitud")
        self.ax1.grid(True, which="both", alpha=0.3)
        lines, labels = self.ax1.get_legend_handles_labels()
        if ax2:
            l2, lb2 = ax2.get_legend_handles_labels()
            lines += l2; labels += lb2
        if labels: self.ax1.legend(lines, labels, loc="best")
        self.ax1.set_title("Gráfico de mediciones")
        self.canvas.draw()

    def _refresh_all(self):
        self.df = ensure_default_cols(normalize_df(self.df))
        self._refresh_tree(); self._refresh_plot()
        self._update_title()

    def _status_text(self):
        base = self.base_path.with_suffix(".csv") if self.base_path else "(sin archivo)"
        return f"Filas: {len(self.df)} | Columnas: {len(self.df.columns)} | CSV: {base}"

    def _update_title(self):
        suffix = f" — {self.base_path.with_suffix('.csv')}" if self.base_path else ""
        self.title(f"Mediciones — Editor y Gráficos{suffix}")

    # ---------- Edición ----------
    def _edit_cell(self, event):
        item = self.tree.identify_row(event.y)
        colid = self.tree.identify_column(event.x)
        if not item or not colid: return
        col_index = int(colid.replace("#", "")) - 1
        colname = self.df.columns[col_index]
        x, y, w, h = self.tree.bbox(item, colid)
        val = self.tree.item(item, "values")[col_index]
        entry = tk.Entry(self.tree); entry.insert(0, val); entry.place(x=x, y=y, width=w, height=h); entry.focus_set()

        def commit_edit(_=None):
            new_val = entry.get(); entry.destroy()
            row_idx = self.tree.index(item)
            self.df.at[row_idx, colname] = new_val
            if colname in NUMERIC_GUESS:
                self.df[colname] = self.df[colname].map(coerce_float)
            if colname == "timestamp":
                try: self.df["timestamp"] = pd.to_datetime(self.df["timestamp"])
                except: pass
            self.recalc_and_refresh(autosave=True)

        entry.bind("<Return>", commit_edit)
        entry.bind("<Escape>", lambda e: entry.destroy())

    # ---------- Archivo ----------
    def new_file(self):
        self.df = ensure_default_cols(normalize_df(pd.DataFrame(columns=DEFAULT_COLS)))
        self.base_path = None
        self._refresh_all()

    def open_csv(self):
        path = filedialog.askopenfilename(title="Abrir CSV", filetypes=[("CSV", "*.csv"), ("Todos", "*.*")])
        if not path: return
        try:
            df = pd.read_csv(path)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el CSV.\n{e}"); return
        self.df = ensure_default_cols(normalize_df(df))
        self.base_path = Path(path).with_suffix("")  # base sin extensión
        self._refresh_all()

    def save_csv_as(self):
        path = filedialog.asksaveasfilename(title="Guardar como CSV", defaultextension=".csv",
                                            filetypes=[("CSV", "*.csv")])
        if not path: return
        self.base_path = Path(path).with_suffix("")
        self._save_csv_impl()

    def save_csv(self):
        if self.base_path is None:
            self.save_csv_as()
        else:
            self._save_csv_impl()

    def _save_csv_impl(self):
        csv_path = self.base_path.with_suffix(".csv")
        try:
            out = self.df.copy()
            # serializar timestamp a ISO
            if "timestamp" in out.columns:
                out["timestamp"] = pd.to_datetime(out["timestamp"], errors="coerce").dt.strftime("%Y-%m-%d %H:%M:%S")
            out.to_csv(csv_path, index=False, na_rep="")
            self.status.set(f"Guardado: {csv_path}")
            self._update_title()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar CSV.\n{e}")

    def export_excel(self):
        if self.base_path is None:
            path = filedialog.asksaveasfilename(title="Exportar Excel", defaultextension=".xlsx",
                                                filetypes=[("Excel", "*.xlsx")])
            if not path: return
            self.base_path = Path(path).with_suffix("")
        xlsx_path = self.base_path.with_suffix(".xlsx")
        try:
            out = self.df.copy()
            if "timestamp" in out.columns:
                out["timestamp"] = pd.to_datetime(out["timestamp"], errors="coerce")
            out.to_excel(xlsx_path, index=False)
            self.status.set(f"Exportado: {xlsx_path}")
            self._update_title()
        except Exception as e:
            messagebox.showwarning("Aviso", f"No se pudo escribir .xlsx (¿openpyxl instalado?).\n{e}")

    def export_png(self):
        if self.base_path is None:
            path = filedialog.asksaveasfilename(title="Exportar PNG", defaultextension=".png",
                                                filetypes=[("PNG", "*.png")])
            if not path: return
            self.base_path = Path(path).with_suffix("")
        png_path = self.base_path.with_suffix(".png")
        try:
            self._refresh_plot()
            self.canvas.figure.savefig(png_path, dpi=150)
            self.status.set(f"Exportado: {png_path}")
            self._update_title()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar PNG.\n{e}")

    # ---------- Operaciones ----------
    def add_row(self):
        row = {c: "" for c in self.df.columns}
        row["idx"] = len(self.df) + 1
        row["timestamp"] = now_ts()
        self.df = pd.concat([self.df, pd.DataFrame([row])], ignore_index=True)
        self.recalc_and_refresh(autosave=True)

    def del_rows(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Seleccioná al menos una fila."); return
        idxs = sorted([self.tree.index(i) for i in sel], reverse=True)
        self.df.drop(index=idxs, inplace=True)
        self.df.reset_index(drop=True, inplace=True)
        self.df = normalize_df(self.df)
        self.recalc_and_refresh(autosave=True)

    def add_column(self):
        name = simpledialog.askstring("Agregar columna", "Nombre de la nueva variable:")
        if not name: return
        if name in self.df.columns:
            messagebox.showwarning("Aviso", "La columna ya existe."); return
        self.df[name] = ""
        self._refresh_all(); self._autosave()

    def del_column(self):
        name = simpledialog.askstring("Borrar columna", "Nombre de la columna a borrar:")
        if not name or name not in self.df.columns: return
        if name in ("idx", "timestamp"):
            messagebox.showwarning("Aviso", "No podés borrar idx o timestamp."); return
        self.df.drop(columns=[name], inplace=True)
        self._refresh_all(); self._autosave()

    def change_n(self):
        current_n = len(self.df)
        n = simpledialog.askinteger("Cambiar N", f"N actual {current_n}. Nuevo N:", minvalue=1)
        if not n: return
        if n > current_n:
            for _ in range(current_n, n): self.add_row()
        elif n < current_n:
            self.df = self.df.iloc[:n, :].copy()
            self._refresh_all(); self._autosave()

    def recalc_and_refresh(self, autosave=False):
        self.df = recalc_powers(normalize_df(self.df))
        self._refresh_tree(); self._refresh_plot()
        if autosave: self._autosave()

    def _autosave(self):
        if self.autosave and self.base_path is not None:
            self._save_csv_impl()

# ---- main ----
if __name__ == "__main__":
    # pip install pandas matplotlib openpyxl
    app = MedicionesApp()
    app.mainloop()
