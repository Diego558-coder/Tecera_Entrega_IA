import numpy as np
import conjuntos
import motor
import motor_sugeno

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

def dibujar_membresias(fig, axes, canvas, tv, ti, th, td, tid, thd, crisp=None, crisp_s=None):
    datos = [
        ("Temperatura (C)", conjuntos.TEMP_U,  conjuntos.TEMP_MFS,
         conjuntos.TEMP_COLORS,  tv, td),
        ("Tiempo (min)",    conjuntos.TIME_U,  conjuntos.TIME_MFS,
         conjuntos.TIME_COLORS,  ti, tid),
        ("Grosor (cm)",     conjuntos.THICK_U, conjuntos.THICK_MFS,
         conjuntos.THICK_COLORS, th, thd),
        ("Salida (°C internos)",  conjuntos.TERM_U,  conjuntos.TERM_MFS,
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

    fig.tight_layout(pad=1.2, rect=[0, 0.13, 1, 1])

    # Pie de página: dos cuadros — Mamdani (amarillo) arriba, Sugeno (azul) abajo
    for txt in fig.texts:
        txt.remove()
    if crisp is not None:
        nombre_m, _, desc_m = motor.interpretar(crisp)
        fig.text(
            0.5, 0.065,
            f"Mamdani (centroide):  {nombre_m}  |  {crisp:.1f} °C internos  —  {desc_m}",
            ha="center", va="bottom",
            color="#ffd700", fontsize=9, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.45", facecolor="#2d2d2d",
                      edgecolor="#ffd700", alpha=0.92),
        )
    if crisp_s is not None:
        nombre_s, _, desc_s = motor.interpretar(crisp_s)
        fig.text(
            0.5, 0.01,
            f"Sugeno   (media pond.):  {nombre_s}  |  {crisp_s:.1f} °C internos  —  {desc_s}",
            ha="center", va="bottom",
            color="#4a90d9", fontsize=9, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.45", facecolor="#2d2d2d",
                      edgecolor="#4a90d9", alpha=0.92),
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
                   xlabel="Temperatura interna de la carne (°C)")
    ax.set_xlim(40, 100)

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

    ax.axvline(crisp, color="#ffd700", lw=2.5, label=f"Centroide: {crisp:.1f} °C")
    ax.text(crisp + 0.5, 0.62, f"{crisp:.1f} °C",
            color="#ffd700", fontsize=11, fontweight="bold")

    ax.legend(loc="upper right", fontsize=7, facecolor=SBG,
              labelcolor="#c9d1d9", edgecolor=BORDER, framealpha=0.9, ncol=2)
    fig.tight_layout(pad=1.2)
    canvas.draw_idle()


# ─────────────────────────────────────────────────────────────────────────────
# GRÁFICA DE COMPARACIÓN MAMDANI vs SUGENO (pestaña "Comparación")
#
# Muestra el efecto de reducir la base de reglas sobre ambos modelos,
# con las mismas entradas en los tres escenarios:
#   1. Todas las reglas  (64)
#   2. Mitad de reglas   (32) — una de cada dos
#   3. Pocas reglas      (~10) — una de cada seis
# Cada escenario tiene dos barras: Mamdani (azul) y Sugeno (naranja).
# ─────────────────────────────────────────────────────────────────────────────

def dibujar_comparacion(fig, ax, canvas, tv, ti, th):
    todas = conjuntos.RULES                                           # 64 reglas
    mitad = [r for r in conjuntos.RULES
             if r[0] in ("Baja", "Media")]                            # 32 reglas: solo T bajas
    pocas = [r for r in conjuntos.RULES
             if r[0] == "Alta" and r[2] in ("Normal", "Gruesa")]      # 8 reglas: Alta + 2 grosores

    escenarios = [
        (f"Todas ({len(todas)} reg.)",              todas),
        (f"Mitad ({len(mitad)} reg.)\nBaja+Media",  mitad),
        (f"Pocas  ({len(pocas)} reg.)\nAlta+2 gros.", pocas),
    ]

    labels = []
    vals_m = []
    vals_s = []

    for label, reglas in escenarios:
        _, _, _, _, _, _, cm = motor.inferir(tv, ti, th, reglas)
        _, _, _, _, cs       = motor_sugeno.inferir_sugeno(tv, ti, th, reglas)
        labels.append(label)
        vals_m.append(cm)
        vals_s.append(cs)

    ax.cla()
    ax.set_facecolor(SBG)
    for borde in ax.spines.values():
        borde.set_color(BORDER)
    ax.tick_params(colors=FG2, labelsize=8)
    ax.set_title(
        f"Mamdani vs Sugeno — Efecto de reducir la base de reglas  "
        f"(T={tv:.0f}°C  t={ti:.0f}min  g={th:.1f}cm)",
        color=FG, fontsize=8, fontweight="bold", pad=6)
    ax.set_ylabel("Temperatura interna (°C)", color=FG2, fontsize=8)
    ax.set_ylim(0, 115)
    ax.grid(True, alpha=0.14, color=BORDER, axis="y")

    x = np.arange(len(labels))
    w = 0.30

    ax.bar(x - w / 2, vals_m, w, color=ACCENT,    alpha=0.88, label="Mamdani (centroide)")
    ax.bar(x + w / 2, vals_s, w, color="#E8903A", alpha=0.88, label="Sugeno  (media pond.)")

    for i, (m, s) in enumerate(zip(vals_m, vals_s)):
        nom_m = motor.interpretar(m)[0]
        nom_s = motor.interpretar(s)[0]
        ax.text(i - w / 2, m + 2, f"{m:.1f}\n{nom_m}",
                ha="center", fontsize=7, color=ACCENT, fontweight="bold")
        ax.text(i + w / 2, s + 2, f"{s:.1f}\n{nom_s}",
                ha="center", fontsize=7, color="#E8903A", fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.legend(facecolor=SBG, labelcolor="#c9d1d9", edgecolor=BORDER, fontsize=8)

    fig.tight_layout(pad=1.4)
    canvas.draw_idle()
