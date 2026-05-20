import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import conjuntos
import motor
import motor_sugeno
import graficador

BG     = "#1e1e1e"
PANEL  = "#2d2d2d"
FG     = "#f0f0f0"
FG2    = "#aaaaaa"
ACCENT = "#4a90d9"
BORDER = "#444444"


class FuzzyApp(tk.Tk):

    def __init__(self, temp=200, tiempo=45, grosor=2.5):
        super().__init__()
        self.title("Sistema Difuso - Coccion de Carne de Res")
        self.configure(bg=BG)
        self.geometry("1300x750")
        try:
            self.state("zoomed")
        except Exception:
            pass

        self._temp   = float(temp)
        self._tiempo = float(tiempo)
        self._grosor = float(grosor)

        self._rule_vars       = []
        self._rule_act_labels = []

        self._fig1    = None
        self._axes1   = None
        self._canvas1 = None
        self._fig2    = None
        self._ax2     = None
        self._canvas2 = None

        self._construir_area_pestanas()
        self._calcular()

    # ─────────────────────────────────────────────────────────────────────────
    # PESTAÑAS — Membresías, Inferencia, Reglas y Comparación
    # ─────────────────────────────────────────────────────────────────────────

    def _construir_area_pestanas(self):
        area = tk.Frame(self, bg=BG)
        area.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dark.TNotebook",
                        background=BG, borderwidth=0, tabmargins=[0, 0, 0, 0])
        style.configure("Dark.TNotebook.Tab",
                        background=PANEL, foreground=FG2,
                        padding=[14, 6], font=("Segoe UI", 9))
        style.map("Dark.TNotebook.Tab",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", "white")])

        nb = ttk.Notebook(area, style="Dark.TNotebook")
        nb.pack(fill=tk.BOTH, expand=True)

        tab1 = tk.Frame(nb, bg=BG)
        nb.add(tab1, text="  Membresías  ")
        self._fig1  = Figure(facecolor=BG)
        self._axes1 = [self._fig1.add_subplot(2, 2, i + 1) for i in range(4)]
        self._canvas1 = FigureCanvasTkAgg(self._fig1, master=tab1)
        self._canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        tab2 = tk.Frame(nb, bg=BG)
        nb.add(tab2, text="  Inferencia  ")
        self._fig2 = Figure(facecolor=BG)
        self._ax2  = self._fig2.add_subplot(1, 1, 1)
        self._canvas2 = FigureCanvasTkAgg(self._fig2, master=tab2)
        self._canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        tab3 = tk.Frame(nb, bg=BG)
        nb.add(tab3, text="  Reglas (64)  ")
        self._construir_panel_reglas(tab3)

    # ─────────────────────────────────────────────────────────────────────────
    # PANEL DE REGLAS
    # ─────────────────────────────────────────────────────────────────────────

    def _construir_panel_reglas(self, parent):
        barra = tk.Frame(parent, bg=PANEL)
        barra.pack(fill=tk.X)

        tk.Label(barra,
                 text="Base de reglas  —  Si (Temperatura AND Tiempo AND Grosor) Entonces Termino",
                 bg=PANEL, fg=FG,
                 font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=12, pady=8)

        header = tk.Frame(parent, bg="#252525")
        header.pack(fill=tk.X)
        for txt, w in [("   #", 5), ("Temperatura", 13), ("Tiempo", 11),
                       ("Grosor", 14), ("", 3), ("Término", 14), ("Activación", 11)]:
            tk.Label(header, text=txt, bg="#252525", fg=FG2,
                     font=("Consolas", 8, "bold"),
                     width=w, anchor="w").pack(side=tk.LEFT, padx=2, pady=4)

        wrap = tk.Frame(parent, bg=BG)
        wrap.pack(fill=tk.BOTH, expand=True)

        cv = tk.Canvas(wrap, bg=BG, highlightthickness=0)
        sb = tk.Scrollbar(wrap, orient=tk.VERTICAL, command=cv.yview)
        cv.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        cv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        inner  = tk.Frame(cv, bg=BG)
        win_id = cv.create_window((0, 0), window=inner, anchor="nw")

        inner.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.bind("<Configure>",    lambda e: cv.itemconfig(win_id, width=e.width))

        def scroll_rueda(e):
            cv.yview_scroll(int(-1 * (e.delta / 120)), "units")

        cv.bind("<MouseWheel>",    scroll_rueda)
        inner.bind("<MouseWheel>", scroll_rueda)

        self._rule_vars       = []
        self._rule_act_labels = []

        for i, (temp, tiempo, grosor, termino) in enumerate(conjuntos.RULES):
            row_bg = "#222222" if i % 2 == 0 else "#1c1c1c"
            var    = tk.BooleanVar(value=True)
            self._rule_vars.append(var)

            fila = tk.Frame(inner, bg=row_bg)
            fila.pack(fill=tk.X)
            fila.bind("<MouseWheel>", scroll_rueda)

            color_termino = conjuntos.TERM_COLORS.get(termino, FG)

            def hacer_comando(v=var):
                return lambda: self._calcular()

            cb = tk.Checkbutton(fila, variable=var,
                                bg=row_bg, activebackground=row_bg,
                                selectcolor="#3a3a3a", relief=tk.FLAT,
                                command=hacer_comando())
            cb.pack(side=tk.LEFT, padx=(6, 0))
            cb.bind("<MouseWheel>", scroll_rueda)

            for txt, w, fg, negrita in [
                (str(i + 1).rjust(2), 5,  FG2,          False),
                (temp,                13, FG,            False),
                (tiempo,              11, FG,            False),
                (grosor,              14, FG,            False),
                ("→",                  3, FG2,           False),
                (termino,             14, color_termino, True),
            ]:
                lbl = tk.Label(fila, text=txt, bg=row_bg, fg=fg,
                               font=("Consolas", 8, "bold" if negrita else "normal"),
                               width=w, anchor="w")
                lbl.pack(side=tk.LEFT, padx=1)
                lbl.bind("<MouseWheel>", scroll_rueda)

            lbl_act = tk.Label(fila, text="0.000", bg=row_bg, fg=FG2,
                               font=("Consolas", 8), width=11, anchor="w")
            lbl_act.pack(side=tk.LEFT, padx=1)
            lbl_act.bind("<MouseWheel>", scroll_rueda)
            self._rule_act_labels.append(lbl_act)

    # ─────────────────────────────────────────────────────────────────────────
    # PESTAÑA COMPARACIÓN MAMDANI vs SUGENO
    # ─────────────────────────────────────────────────────────────────────────

    def _toggle_todas(self, estado):
        for var in self._rule_vars:
            var.set(estado)
        self._calcular()

    # ─────────────────────────────────────────────────────────────────────────
    # LÓGICA DE CÁLCULO
    # ─────────────────────────────────────────────────────────────────────────

    def _leer_entradas(self):
        tv = max(0.0, min(300.0, round(self._temp   / 5)   * 5.0))
        ti = max(0.0, min(120.0, round(self._tiempo / 5)   * 5.0))
        th = max(0.0, min(6.0,   round(self._grosor / 0.1) * 0.1))
        return tv, ti, th

    def _calcular(self):
        tv, ti, th = self._leer_entradas()

        reglas_activas = [r for r, v in zip(conjuntos.RULES, self._rule_vars) if v.get()]

        td, tid, thd, acts, _, agregado, crisp = motor.inferir(tv, ti, th, reglas_activas)
        _, _, _, _, crisp_s = motor_sugeno.inferir_sugeno(tv, ti, th, reglas_activas)

        for i, (t, ti_r, th_r, _) in enumerate(conjuntos.RULES):
            act       = min(td.get(t, 0), tid.get(ti_r, 0), thd.get(th_r, 0))
            is_active = self._rule_vars[i].get()

            if not is_active:
                color_act = "#444444"
            elif act > 0.005:
                color_act = "#ffd700"
            else:
                color_act = FG2

            self._rule_act_labels[i].config(text=f"{act:.3f}", fg=color_act)

        graficador.dibujar_membresias(
            self._fig1, self._axes1, self._canvas1,
            tv, ti, th, td, tid, thd, crisp, crisp_s)
        graficador.dibujar_salida(
            self._fig2, self._ax2, self._canvas2,
            agregado, crisp, acts)
