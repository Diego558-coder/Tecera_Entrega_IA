import numpy as np
import conjuntos


class Graficador:
    """Dibuja las dos secciones de la vista unica:
    funciones de membresia (arriba) y salida defuzzificada (abajo)."""

    BG     = "#1e1e1e"
    SBG    = "#2d2d2d"
    FG     = "#f0f0f0"
    FG2    = "#aaaaaa"
    BORDER = "#444444"
    ACCENT = "#4a90d9"

    def __init__(self, fig1, axes1, canvas1, fig2, ax2, canvas2):
        self.fig1    = fig1
        self.axes1   = axes1
        self.canvas1 = canvas1
        self.fig2    = fig2
        self.ax2     = ax2
        self.canvas2 = canvas2

    # ── Estilo oscuro comun ───────────────────────────────────────────────────
    def _estilo(self, ax, titulo, xlabel=""):
        ax.set_facecolor(self.SBG)
        for sp in ax.spines.values():
            sp.set_color(self.BORDER)
        ax.tick_params(colors=self.FG2, labelsize=7)
        ax.set_title(titulo, color=self.FG, fontsize=8, fontweight="bold", pad=4)
        ax.set_ylabel("Membresia", color=self.FG2, fontsize=7)
        ax.set_ylim(-0.05, 1.18)
        ax.grid(True, alpha=0.14, color=self.BORDER)
        if xlabel:
            ax.set_xlabel(xlabel, color=self.FG2, fontsize=7)

    # ── Seccion superior: 4 funciones de membresia ───────────────────────────
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
                            ax.plot(val, deg, "o", color=col, ms=5, zorder=6,
                                    markeredgecolor="white", markeredgewidth=0.4)
                            ax.text(val + span * 0.02, deg + 0.05,
                                    f"{deg:.2f}", color=col, fontsize=6)
            ax.legend(loc="upper right", fontsize=6, facecolor=self.SBG,
                      labelcolor="#c9d1d9", edgecolor=self.BORDER, framealpha=0.85)
        self.fig1.tight_layout(pad=1.2)
        self.canvas1.draw_idle()

    # ── Seccion inferior: salida agregada + centroide ─────────────────────────
    def dibujar_salida(self, agregado, crisp, activaciones):
        ax = self.ax2
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
        self.fig2.tight_layout(pad=1.2)
        self.canvas2.draw_idle()
