import numpy as np
import conjuntos
import motor

# Paleta de colores compartida con la aplicación
BG     = "#1e1e1e"
SBG    = "#2d2d2d"
FG     = "#f0f0f0"
FG2    = "#aaaaaa"
BORDER = "#444444"
ACCENT = "#4a90d9"


# ─────────────────────────────────────────────────────────────────────────────
# ESTILO COMÚN
#
# Aplica el tema oscuro a cualquier eje de matplotlib para mantener
# consistencia visual en todas las gráficas.
# ─────────────────────────────────────────────────────────────────────────────

def aplicar_estilo(ax, titulo, xlabel=""):
    ax.set_facecolor(SBG)
    for borde in ax.spines.values():
        borde.set_color(BORDER)
    ax.tick_params(colors=FG2, labelsize=7)
    ax.set_title(titulo, color=FG, fontsize=8, fontweight="bold", pad=4)
    ax.set_ylabel("Membresia", color=FG2, fontsize=7)
    ax.set_ylim(-0.05, 1.18)
    ax.grid(True, alpha=0.14, color=BORDER)
    if xlabel:
        ax.set_xlabel(xlabel, color=FG2, fontsize=7)


# ─────────────────────────────────────────────────────────────────────────────
# GRÁFICA DE FUNCIONES DE MEMBRESÍA (pestaña "Membresías")
#
# Dibuja las 4 subgráficas: temperatura, tiempo, grosor y salida.
# Para las tres entradas, además marca con una línea vertical el valor actual
# y un punto sobre cada conjunto que esté activo.
#
# Parámetros:
#   fig, axes, canvas — objetos matplotlib de la pestaña
#   tv, ti, th        — valores actuales de temperatura, tiempo y grosor
#   td, tid, thd      — grados de membresía resultantes de la fuzzificación
# ─────────────────────────────────────────────────────────────────────────────

def dibujar_membresias(fig, axes, canvas, tv, ti, th, td, tid, thd, crisp=None):
    datos = [
        ("Temperatura (C)", conjuntos.TEMP_U,  conjuntos.TEMP_MFS,
         conjuntos.TEMP_COLORS,  tv, td),
        ("Tiempo (min)",    conjuntos.TIME_U,  conjuntos.TIME_MFS,
         conjuntos.TIME_COLORS,  ti, tid),
        ("Grosor (cm)",     conjuntos.THICK_U, conjuntos.THICK_MFS,
         conjuntos.THICK_COLORS, th, thd),
        ("Salida (0-100)",  conjuntos.TERM_U,  conjuntos.TERM_MFS,
         list(conjuntos.TERM_COLORS.values()), crisp, None),
    ]

    for ax, (titulo, universo, mfs, colores, val, grados) in zip(axes, datos):
        ax.cla()
        aplicar_estilo(ax, titulo)

        # Dibujamos cada conjunto con su color y relleno suave
        for (nombre, mf), color in zip(mfs.items(), colores):
            ax.plot(universo, mf, color=color, lw=1.8, label=nombre)
            ax.fill_between(universo, mf, alpha=0.12, color=color)

        # Si hay un valor de entrada, lo marcamos
        if val is not None:
            ax.axvline(val, color=FG, lw=1.3, ls="--", alpha=0.85)

            if grados:
                span = universo[-1] - universo[0]
                for (nombre, deg), color in zip(grados.items(), colores):
                    if deg > 0.005:
                        # Punto sobre la curva en el valor actual
                        ax.plot(val, deg, "o", color=color, ms=5, zorder=6,
                                markeredgecolor="white", markeredgewidth=0.4)
                        # Etiqueta con el grado de pertenencia
                        ax.text(val + span * 0.02, deg + 0.05,
                                f"{deg:.2f}", color=color, fontsize=6)

        ax.legend(loc="upper right", fontsize=6, facecolor=SBG,
                  labelcolor="#c9d1d9", edgecolor=BORDER, framealpha=0.85)

    fig.tight_layout(pad=1.2, rect=[0, 0.07, 1, 1])

    # Pie de página con el resultado
    for txt in fig.texts:
        txt.remove()
    if crisp is not None:
        nombre, _, desc = motor.interpretar(crisp)
        fig.text(
            0.5, 0.01,
            f"Resultado:  {nombre}  |  {crisp:.1f} / 100  —  {desc}",
            ha="center", va="bottom",
            color="#ffd700", fontsize=9, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#2d2d2d",
                      edgecolor="#ffd700", alpha=0.92),
        )

    canvas.draw_idle()


# ─────────────────────────────────────────────────────────────────────────────
# GRÁFICA DE INFERENCIA Y DEFUZZIFICACIÓN (pestaña "Inferencia")
#
# Muestra el área agregada resultante de combinar todos los conjuntos
# activados, y la línea vertical del centroide (valor crisp final).
#
# Parámetros:
#   fig, ax, canvas — objetos matplotlib de la pestaña
#   agregado        — arreglo numpy con el área total agregada
#   crisp           — valor numérico del centroide
#   activaciones    — diccionario {término: nivel_de_activación}
# ─────────────────────────────────────────────────────────────────────────────

def dibujar_salida(fig, ax, canvas, agregado, crisp, activaciones):
    ax.cla()
    aplicar_estilo(ax,
                   "Membresia Agregada  —  Defuzzificacion por Centroide",
                   xlabel="Termino de coccion (0-100)")
    ax.set_xlim(0, 100)

    for nombre, color in conjuntos.TERM_COLORS.items():
        ax.plot(conjuntos.TERM_U, conjuntos.TERM_MFS[nombre],
                color=color, lw=1, ls=":", alpha=0.3)

    for nombre, color in conjuntos.TERM_COLORS.items():
        fuerza = activaciones.get(nombre, 0)
        if fuerza > 0.005:
            area = np.fmin(fuerza, conjuntos.TERM_MFS[nombre])
            ax.fill_between(conjuntos.TERM_U, area,
                            alpha=0.5, color=color,
                            label=f"{nombre} ({fuerza:.3f})")

    ax.fill_between(conjuntos.TERM_U, agregado, alpha=0.12, color=ACCENT)
    ax.plot(conjuntos.TERM_U, agregado, color=ACCENT, lw=2, label="Area agregada")

    ax.axvline(crisp, color="#ffd700", lw=2.5, label=f"Centroide: {crisp:.1f}")
    ax.text(crisp + 1, 0.62, f"{crisp:.1f}",
            color="#ffd700", fontsize=11, fontweight="bold")

    ax.legend(loc="upper right", fontsize=7, facecolor=SBG,
              labelcolor="#c9d1d9", edgecolor=BORDER, framealpha=0.9, ncol=2)
    fig.tight_layout(pad=1.2)
    canvas.draw_idle()
