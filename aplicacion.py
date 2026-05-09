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

        self._motor           = MotorDifuso()
        self._graficador      = None
        self._spins           = {}
        self._rule_vars       = []   # BooleanVar por regla
        self._rule_act_labels = []   # Label de activacion por regla

        self._construir_panel_izquierdo()
        self._construir_area_pestanas()
        self._calcular()

    # ── Panel izquierdo ───────────────────────────────────────────────────────
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
            ("temp",  "Temperatura del Horno (C):", 0,   300, 5,   200),
            ("time",  "Tiempo de Coccion (min):",    0,   120, 5,    45),
            ("thick", "Grosor de la Carne (cm):",    0.0, 6.0, 0.1,  2.5),
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

        self._res_box  = tk.Frame(panel, bg="#8B0000", padx=10, pady=8)
        self._res_box.pack(fill=tk.X, padx=14, pady=4)
        self._lbl_term = tk.Label(self._res_box, text="—",
                                   bg="#8B0000", fg="white",
                                   font=("Segoe UI", 14, "bold"))
        self._lbl_term.pack()
        self._lbl_score = tk.Label(self._res_box, text="",
                                    bg="#8B0000", fg="#eeeeee",
                                    font=("Segoe UI", 9))
        self._lbl_score.pack()
        self._lbl_desc = tk.Label(self._res_box, text="",
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

    # ── Pestanas ──────────────────────────────────────────────────────────────
    def _construir_area_pestanas(self):
        area = tk.Frame(self, bg=self.BG)
        area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(4, 8), pady=8)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dark.TNotebook",
                        background=self.BG, borderwidth=0, tabmargins=[0, 0, 0, 0])
        style.configure("Dark.TNotebook.Tab",
                        background=self.PANEL, foreground=self.FG2,
                        padding=[14, 6], font=("Segoe UI", 9))
        style.map("Dark.TNotebook.Tab",
                  background=[("selected", self.ACCENT)],
                  foreground=[("selected", "white")])

        nb = ttk.Notebook(area, style="Dark.TNotebook")
        nb.pack(fill=tk.BOTH, expand=True)

        # Pestana 1 — Funciones de membresia
        tab1 = tk.Frame(nb, bg=self.BG)
        nb.add(tab1, text="  Membresías  ")
        fig1  = Figure(facecolor=self.BG)
        axes1 = [fig1.add_subplot(2, 2, i + 1) for i in range(4)]
        c1    = FigureCanvasTkAgg(fig1, master=tab1)
        c1.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Pestana 2 — Inferencia / salida
        tab2 = tk.Frame(nb, bg=self.BG)
        nb.add(tab2, text="  Inferencia  ")
        fig2 = Figure(facecolor=self.BG)
        ax2  = fig2.add_subplot(1, 1, 1)
        c2   = FigureCanvasTkAgg(fig2, master=tab2)
        c2.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self._graficador = Graficador(fig1, axes1, c1, fig2, ax2, c2)

        # Pestana 3 — Reglas
        tab3 = tk.Frame(nb, bg=self.BG)
        nb.add(tab3, text="  Reglas (64)  ")
        self._construir_panel_reglas(tab3)

    # ── Panel de reglas ───────────────────────────────────────────────────────
    def _construir_panel_reglas(self, parent):
        # Barra superior con botones globales
        barra = tk.Frame(parent, bg=self.PANEL)
        barra.pack(fill=tk.X)

        tk.Label(barra, text="Base de reglas  —  Si (Temperatura AND Tiempo AND Grosor) Entonces Termino",
                 bg=self.PANEL, fg=self.FG,
                 font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=12, pady=8)

        tk.Button(barra, text="Activar todas",
                  bg="#2a5c2a", fg="white", font=("Segoe UI", 8),
                  relief=tk.FLAT, padx=10, pady=3, cursor="hand2",
                  command=lambda: self._toggle_todas(True)).pack(side=tk.RIGHT, padx=(4, 12), pady=6)
        tk.Button(barra, text="Desactivar todas",
                  bg="#5c2a2a", fg="white", font=("Segoe UI", 8),
                  relief=tk.FLAT, padx=10, pady=3, cursor="hand2",
                  command=lambda: self._toggle_todas(False)).pack(side=tk.RIGHT, padx=4, pady=6)

        # Encabezado de columnas
        header = tk.Frame(parent, bg="#252525")
        header.pack(fill=tk.X)
        for txt, w in [("   #", 5), ("Temperatura", 13), ("Tiempo", 11),
                       ("Grosor", 14), ("", 3), ("Término", 14), ("Activación", 11)]:
            tk.Label(header, text=txt, bg="#252525", fg=self.FG2,
                     font=("Consolas", 8, "bold"),
                     width=w, anchor="w").pack(side=tk.LEFT, padx=2, pady=4)

        # Area scrollable
        wrap = tk.Frame(parent, bg=self.BG)
        wrap.pack(fill=tk.BOTH, expand=True)

        cv = tk.Canvas(wrap, bg=self.BG, highlightthickness=0)
        sb = tk.Scrollbar(wrap, orient=tk.VERTICAL, command=cv.yview)
        cv.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        cv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        inner = tk.Frame(cv, bg=self.BG)
        win_id = cv.create_window((0, 0), window=inner, anchor="nw")

        inner.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.bind("<Configure>",    lambda e: cv.itemconfig(win_id, width=e.width))

        def _scroll(e):
            cv.yview_scroll(int(-1 * (e.delta / 120)), "units")

        cv.bind("<MouseWheel>", _scroll)
        inner.bind("<MouseWheel>", _scroll)

        # Filas de reglas
        self._rule_vars       = []
        self._rule_act_labels = []

        for i, (temp, tiempo, grosor, termino) in enumerate(conjuntos.RULES):
            row_bg = "#222222" if i % 2 == 0 else "#1c1c1c"
            var = tk.BooleanVar(value=True)
            self._rule_vars.append(var)

            row = tk.Frame(inner, bg=row_bg)
            row.pack(fill=tk.X)
            row.bind("<MouseWheel>", _scroll)

            tc = conjuntos.TERM_COLORS.get(termino, self.FG)

            def make_cb_cmd(v=var):
                return lambda: self._calcular()

            cb = tk.Checkbutton(row, variable=var,
                                bg=row_bg, activebackground=row_bg,
                                selectcolor="#3a3a3a", relief=tk.FLAT,
                                command=make_cb_cmd())
            cb.pack(side=tk.LEFT, padx=(6, 0))
            cb.bind("<MouseWheel>", _scroll)

            for txt, w, fg, bold in [
                (str(i + 1).rjust(2), 5,  self.FG2, False),
                (temp,               13, self.FG,  False),
                (tiempo,             11, self.FG,  False),
                (grosor,             14, self.FG,  False),
                ("→",                 3, self.FG2, False),
                (termino,            14, tc,        True),
            ]:
                lbl = tk.Label(row, text=txt, bg=row_bg, fg=fg,
                               font=("Consolas", 8, "bold" if bold else "normal"),
                               width=w, anchor="w")
                lbl.pack(side=tk.LEFT, padx=1)
                lbl.bind("<MouseWheel>", _scroll)

            lbl_act = tk.Label(row, text="0.000", bg=row_bg, fg=self.FG2,
                               font=("Consolas", 8), width=11, anchor="w")
            lbl_act.pack(side=tk.LEFT, padx=1)
            lbl_act.bind("<MouseWheel>", _scroll)
            self._rule_act_labels.append(lbl_act)

    def _toggle_todas(self, estado):
        for var in self._rule_vars:
            var.set(estado)
        self._calcular()

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

        reglas_activas = [r for r, v in zip(conjuntos.RULES, self._rule_vars)
                          if v.get()]

        td, tid, thd, acts, _, agregado, crisp = self._motor.inferir(
            tv, ti, th, reglas_activas)
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

        # Actualizar activacion de todas las reglas (incluyendo desactivadas)
        for i, (t, ti_r, th_r, _) in enumerate(conjuntos.RULES):
            act        = min(td.get(t, 0), tid.get(ti_r, 0), thd.get(th_r, 0))
            is_active  = self._rule_vars[i].get()
            if not is_active:
                fg_act = "#444444"
            elif act > 0.005:
                fg_act = "#ffd700"
            else:
                fg_act = self.FG2
            self._rule_act_labels[i].config(text=f"{act:.3f}", fg=fg_act)

        self._graficador.dibujar_membresias(tv, ti, th, td, tid, thd)
        self._graficador.dibujar_salida(agregado, crisp, acts)
