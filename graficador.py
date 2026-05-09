import numpy as np
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap, BoundaryNorm
import conjuntos


class Graficador:
    """Dibuja las tres vistas matplotlib dentro de la ventana:
    funciones de membresia, matriz de reglas y salida defuzzificada."""

    BG     = "#0d1117"
    SBG    = "#161b22"
    FG     = "#e6edf3"
    FG2    = "#8b949e"
    BORDER = "#30363d"
    ACCENT = "#58a6ff"

    def __init__(self, fig1, axes1, canvas1,
                 fig2, axes2, canvas2,
                 fig3, ax3,   canvas3):
        self.fig1    = fig1;  self.axes1   = axes1;  self.canvas1 = canvas1
        self.fig2    = fig2;  self.axes2   = axes2;  self.canvas2 = canvas2
        self.fig3    = fig3;  self.ax3     = ax3;    self.canvas3 = canvas3

    # ── Estilo oscuro comun ───────────────────────────────────────────────────
    def _estilo(self, ax, titulo, xlabel=""):
        ax.set_facecolor(self.SBG)
        for sp in ax.spines.values():
            sp.set_color(self.BORDER)
        ax.tick_params(colors=self.FG2, labelsize=7)
        ax.set_title(titulo, color=self.FG, fontsize=9, fontweight="bold", pad=5)
        ax.set_ylabel("Membresia", color=self.FG2, fontsize=7)
        ax.set_ylim(-0.05, 1.18)
        ax.grid(True, alpha=0.14, color=self.BORDER)
        if xlabel:
            ax.set_xlabel(xlabel, color=self.FG2, fontsize=7)

    # ── Tab 1: funciones de membresia (se actualiza con cada slider) ──────────
    def dibujar_membresias(self, tv, ti, th, td, tid, thd):
        datos = [
            ("Temperatura (C)", conjuntos.TEMP_U,  conjuntos.TEMP_MFS,
             conjuntos.TEMP_COLORS,  tv, td),
            ("Tiempo (min)",    conjuntos.TIME_U,  conjuntos.TIME_MFS,
             conjuntos.TIME_COLORS,  ti, tid),
            ("Grosor (cm)",     conjuntos.THICK_U, conjuntos.THICK_MFS,
             conjuntos.THICK_COLORS, th, thd),
            ("Salida (0-100)",  conjuntos.TERM_U,  conjuntos.TERM_MFS,
             list(conjuntos.TERM_COLORS.values()), None, None),
        ]
        for ax, (titulo, uni, mfs, cols, val, degs) in zip(self.axes1, datos):
            ax.cla()
            self._estilo(ax, titulo)
            for (nombre, mf), col in zip(mfs.items(), cols):
                ax.plot(uni, mf, color=col, lw=1.8, label=nombre)
                ax.fill_between(uni, mf, alpha=0.12, color=col)
            if val is not None:
                ax.axvline(val, color=self.FG, lw=1.3, ls="--", alpha=0.85)
                if degs:
                    span = uni[-1] - uni[0]
                    for (nombre, deg), col in zip(degs.items(), cols):
                        if deg > 0.005:
                            ax.plot(val, deg, "o", color=col, ms=6, zorder=6,
                                    markeredgecolor="white", markeredgewidth=0.4)
                            ax.text(val + span * 0.02, deg + 0.05,
                                    f"{deg:.2f}", color=col, fontsize=6)
            ax.legend(loc="upper right", fontsize=6, facecolor=self.SBG,
                      labelcolor="#c9d1d9", edgecolor=self.BORDER, framealpha=0.85)
        self.fig1.tight_layout(pad=1.6)
        self.canvas1.draw_idle()

    # ── Tab 3: salida agregada + centroide (se actualiza con cada slider) ─────
    def dibujar_salida(self, agregado, crisp, activaciones):
        ax = self.ax3
        ax.cla()
        self._estilo(ax, "Membresia Agregada  —  Defuzzificacion por Centroide",
                     xlabel="Termino de coccion (0-100)")
        ax.set_xlim(0, 100)

        for nombre, col in conjuntos.TERM_COLORS.items():
            ax.plot(conjuntos.TERM_U, conjuntos.TERM_MFS[nombre],
                    color=col, lw=1, ls=":", alpha=0.3)

        for nombre, col in conjuntos.TERM_COLORS.items():
            fuerza = activaciones.get(nombre, 0)
            if fuerza > 0.005:
                ax.fill_between(conjuntos.TERM_U,
                                np.fmin(fuerza, conjuntos.TERM_MFS[nombre]),
                                alpha=0.5, color=col,
                                label=f"{nombre} ({fuerza:.3f})")

        ax.fill_between(conjuntos.TERM_U, agregado, alpha=0.12, color=self.ACCENT)
        ax.plot(conjuntos.TERM_U, agregado, color=self.ACCENT, lw=2,
                label="Area agregada")
        ax.axvline(crisp, color="#ffd700", lw=2.5,
                   label=f"Centroide: {crisp:.1f}")
        ax.text(crisp + 1, 0.62, f"{crisp:.1f}",
                color="#ffd700", fontsize=11, fontweight="bold")
        ax.legend(loc="upper right", fontsize=7, facecolor=self.SBG,
                  labelcolor="#c9d1d9", edgecolor=self.BORDER,
                  framealpha=0.9, ncol=2)
        self.fig3.tight_layout(pad=1.5)
        self.canvas3.draw_idle()

    # ── Tab 2: matriz de reglas (solo se dibuja una vez al iniciar) ───────────
    def dibujar_matriz_reglas(self):
        TL = ["Baja", "Media", "Alta", "Muy Alta"]
        IL = ["Poco", "Moderado", "Mucho", "Excesivo"]
        GL = ["Delgada", "Normal", "Gruesa", "Muy Gruesa"]

        t2n  = {t: i for i, t in enumerate(conjuntos.TERM_COLORS)}
        rd   = {(t, ti, th): out for (t, ti, th, out) in conjuntos.RULES}
        cmap = ListedColormap(list(conjuntos.TERM_COLORS.values()))
        norm = BoundaryNorm(np.arange(-0.5, 6.5, 1), cmap.N)

        self.fig2.suptitle("Matriz de Reglas  (Temperatura x Tiempo  por Grosor)",
                            color=self.FG, fontsize=10, fontweight="bold")

        for ax, grosor in zip(self.axes2, GL):
            mat = np.array([[t2n[rd[(temp, tiempo, grosor)]] for temp in TL]
                            for tiempo in IL], dtype=float)
            ax.imshow(mat, cmap=cmap, norm=norm, aspect="auto")
            ax.set_facecolor(self.SBG)
            ax.set_xticks(range(len(TL)));  ax.set_xticklabels(TL, color="#c9d1d9", fontsize=8)
            ax.set_yticks(range(len(IL)));  ax.set_yticklabels(IL, color="#c9d1d9", fontsize=8)
            ax.set_title(f"Grosor: {grosor}", color=self.FG, fontweight="bold", fontsize=9)
            ax.set_xlabel("Temperatura", color=self.FG2, fontsize=8)
            ax.set_ylabel("Tiempo",      color=self.FG2, fontsize=8)
            ax.tick_params(colors=self.FG2)
            for i, tiempo in enumerate(IL):
                for j, temp in enumerate(TL):
                    etiq = rd[(temp, tiempo, grosor)]
                    corta = etiq.replace("Tres Cuartos", "T.C").replace("Bien Cocido", "B.C")
                    ax.text(j, i, corta, ha="center", va="center",
                            color="white", fontsize=7.5, fontweight="bold")

        parches = [mpatches.Patch(color=c, label=t)
                   for t, c in conjuntos.TERM_COLORS.items()]
        self.fig2.legend(handles=parches, loc="lower center", ncol=6,
                         facecolor=self.SBG, labelcolor="#c9d1d9",
                         edgecolor=self.BORDER, fontsize=8,
                         bbox_to_anchor=(0.5, 0.01))
        self.fig2.tight_layout(rect=[0, 0.07, 1, 0.95])
        self.canvas2.draw()
