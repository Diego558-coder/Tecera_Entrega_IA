import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import conjuntos
from motor import MotorDifuso
from graficador import Graficador


class FuzzyApp(tk.Tk):
    """Ventana unica: panel de controles a la izquierda,
    graficas de membresia arriba e inferencia abajo a la derecha."""

    BG     = "#1e1e1e"
    PANEL  = "#2d2d2d"
    FG     = "#f0f0f0"
    FG2    = "#aaaaaa"
    ACCENT = "#4a90d9"
    BORDER = "#444444"

    def __init__(self):
        super().__init__()
        self.title("Sistema Difuso - Coccion de Carne de Res")
        self.configure(bg=self.BG)
        self.geometry("1300x750")
        try:
            self.state("zoomed")
        except Exception:
            pass

        self._motor      = MotorDifuso()
        self._graficador = None
        self._spins      = {}

        self._construir_panel_izquierdo()
        self._construir_area_graficas()
        self._calcular()

    # ── Panel izquierdo: entradas + resultado ─────────────────────────────────
    def _construir_panel_izquierdo(self):
        panel = tk.Frame(self, bg=self.PANEL, width=260)
        panel.pack(side=tk.LEFT, fill=tk.Y, padx=(8, 4), pady=8)
        panel.pack_propagate(False)

        tk.Label(panel, text="Sistema Difuso",
                 bg=self.PANEL, fg=self.FG,
                 font=("Segoe UI", 12, "bold")).pack(pady=(14, 2))
        tk.Label(panel, text="Coccion de Carne de Res",
                 bg=self.PANEL, fg=self.FG2,
                 font=("Segoe UI", 8)).pack(pady=(0, 12))
        tk.Frame(panel, bg=self.BORDER, height=1).pack(fill=tk.X, padx=10)

        entradas = [
            ("temp",  "Temperatura del Horno (C):",  0,   300, 5,   200),
            ("time",  "Tiempo de Coccion (min):",     0,   120, 5,    45),
            ("thick", "Grosor de la Carne (cm):",     0.0, 6.0, 0.1,  2.5),
        ]
        for clave, etiqueta, lo, hi, paso, ini in entradas:
            tk.Label(panel, text=etiqueta,
                     bg=self.PANEL, fg=self.FG2,
                     font=("Segoe UI", 8)).pack(anchor="w", padx=14, pady=(10, 1))
            sp = tk.Spinbox(panel, from_=lo, to=hi, increment=paso,
                            width=10, font=("Segoe UI", 10),
                            bg="#3c3c3c", fg=self.FG,
                            buttonbackground="#444",
                            relief=tk.FLAT, bd=1,
                            highlightthickness=1,
                            highlightcolor=self.ACCENT,
                            highlightbackground=self.BORDER)
            sp.delete(0, tk.END)
            sp.insert(0, str(ini))
            sp.pack(padx=14, anchor="w")
            sp.bind("<Return>",   lambda e: self._calcular())
            sp.bind("<FocusOut>", lambda e: self._calcular())
            self._spins[clave] = sp

        tk.Frame(panel, bg=self.BORDER, height=1).pack(fill=tk.X, padx=10, pady=12)

        tk.Button(panel, text="Calcular",
                  bg=self.ACCENT, fg="white",
                  font=("Segoe UI", 9, "bold"),
                  relief=tk.FLAT, padx=12, pady=5, cursor="hand2",
                  command=self._calcular).pack(padx=14, fill=tk.X)

        tk.Frame(panel, bg=self.BORDER, height=1).pack(fill=tk.X, padx=10, pady=10)
        tk.Label(panel, text="Resultado:",
                 bg=self.PANEL, fg=self.FG2,
                 font=("Segoe UI", 8)).pack(anchor="w", padx=14)

        self._res_box   = tk.Frame(panel, bg="#8B0000", padx=10, pady=8)
        self._res_box.pack(fill=tk.X, padx=14, pady=4)
        self._lbl_term  = tk.Label(self._res_box, text="—",
                                    bg="#8B0000", fg="white",
                                    font=("Segoe UI", 14, "bold"))
        self._lbl_term.pack()
        self._lbl_score = tk.Label(self._res_box, text="",
                                    bg="#8B0000", fg="#eeeeee",
                                    font=("Segoe UI", 9))
        self._lbl_score.pack()
        self._lbl_desc  = tk.Label(self._res_box, text="",
                                    bg="#8B0000", fg="#cccccc",
                                    font=("Segoe UI", 7),
                                    wraplength=220, justify=tk.CENTER)
        self._lbl_desc.pack(pady=(2, 0))

        tk.Frame(panel, bg=self.BORDER, height=1).pack(fill=tk.X, padx=10, pady=8)
        tk.Label(panel, text="Membresias activas:",
                 bg=self.PANEL, fg=self.FG2,
                 font=("Segoe UI", 7)).pack(anchor="w", padx=14)
        self._memb_box = tk.Frame(panel, bg=self.PANEL)
        self._memb_box.pack(fill=tk.X, padx=14, pady=2)

    # ── Area derecha: graficas en vista unica (arriba + abajo) ───────────────
    def _construir_area_graficas(self):
        area = tk.Frame(self, bg=self.BG)
        area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(4, 8), pady=8)

        # Seccion superior — 4 funciones de membresia
        marco_sup = tk.Frame(area, bg=self.BG)
        marco_sup.pack(fill=tk.BOTH, expand=True)

        fig1  = Figure(facecolor=self.BG)
        axes1 = [fig1.add_subplot(2, 2, i + 1) for i in range(4)]
        c1    = FigureCanvasTkAgg(fig1, master=marco_sup)
        c1.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Separador visual
        tk.Frame(area, bg=self.BORDER, height=1).pack(fill=tk.X, pady=2)

        # Seccion inferior — salida defuzzificada
        marco_inf = tk.Frame(area, bg=self.BG)
        marco_inf.pack(fill=tk.BOTH, expand=True)

        fig2 = Figure(facecolor=self.BG)
        ax2  = fig2.add_subplot(1, 1, 1)
        c2   = FigureCanvasTkAgg(fig2, master=marco_inf)
        c2.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self._graficador = Graficador(fig1, axes1, c1, fig2, ax2, c2)

    # ── Logica ────────────────────────────────────────────────────────────────
    def _leer_entradas(self):
        try:
            tv = float(self._spins["temp"].get())
            ti = float(self._spins["time"].get())
            th = float(self._spins["thick"].get())
        except ValueError:
            return None, None, None
        tv = max(0.0, min(300.0, round(tv / 5)   * 5.0))
        ti = max(0.0, min(120.0, round(ti / 5)   * 5.0))
        th = max(0.0, min(6.0,   round(th / 0.1) * 0.1))
        return tv, ti, th

    def _calcular(self, event=None):
        tv, ti, th = self._leer_entradas()
        if tv is None:
            return

        td, tid, thd, acts, _, agregado, crisp = self._motor.inferir(tv, ti, th)
        nombre, color, desc = self._motor.interpretar(crisp)

        for w in (self._res_box, self._lbl_term, self._lbl_score, self._lbl_desc):
            w.config(bg=color)
        self._lbl_term.config(text=nombre)
        self._lbl_score.config(text=f"{crisp:.1f} / 100")
        self._lbl_desc.config(text=desc)

        for w in self._memb_box.winfo_children():
            w.destroy()
        for prefijo, degs, cols in [("T",  td,  conjuntos.TEMP_COLORS),
                                     ("Ti", tid, conjuntos.TIME_COLORS),
                                     ("G",  thd, conjuntos.THICK_COLORS)]:
            for (nom, deg), col in zip(degs.items(), cols):
                if deg > 0.005:
                    tk.Label(self._memb_box,
                             text=f"{prefijo}: {nom} = {deg:.3f}",
                             bg=self.PANEL, fg=col,
                             font=("Segoe UI", 7)).pack(anchor="w")

        self._graficador.dibujar_membresias(tv, ti, th, td, tid, thd)
        self._graficador.dibujar_salida(agregado, crisp, acts)
