import numpy as np
import skfuzzy as fuzz
import conjuntos

# ─────────────────────────────────────────────────────────────────────────────
# FUZZIFICACIÓN
#
# Convierte un valor numérico (crisp) en grados de pertenencia para cada
# conjunto difuso de una variable. Por ejemplo, 180°C puede pertenecer
# parcialmente a "Media" y parcialmente a "Alta" al mismo tiempo.
#
# Parámetros:
#   valor    — el valor numérico a fuzzificar
#   mf_dict  — diccionario {nombre: arreglo_membresía}
#   universo — arreglo numpy con los valores posibles de la variable
#
# Retorna:
#   diccionario {nombre_conjunto: grado_de_pertenencia}
# ─────────────────────────────────────────────────────────────────────────────

def fuzzificar(valor, mf_dict, universo):
    # Aseguramos que el valor esté dentro del rango del universo
    v = float(np.clip(valor, universo[0], universo[-1]))

    grados = {}
    for nombre, mf in mf_dict.items():
        # interp_membership busca el grado de pertenencia interpolando en la curva
        grados[nombre] = float(fuzz.interp_membership(universo, mf, v))
    return grados


# ─────────────────────────────────────────────────────────────────────────────
# INFERENCIA MAMDANI
#
# Aplica el proceso completo de inferencia difusa:
#   1. Fuzzificación de las tres entradas
#   2. Evaluación de cada regla con AND = mínimo de los tres grados
#   3. Agregación: para el mismo término de salida, nos quedamos con el máximo
#   4. Construcción del área agregada (recorte al nivel de activación)
#   5. Defuzzificación por centroide → valor crisp final
#
# Parámetros:
#   temp, tiempo, grosor — valores numéricos de las entradas
#   reglas               — lista de reglas activas (por defecto, todas)
#
# Retorna una tupla con los resultados intermedios y el valor crisp final.
# ─────────────────────────────────────────────────────────────────────────────

def inferir(temp, tiempo, grosor, reglas=None):
    if reglas is None:
        reglas = conjuntos.RULES

    # Paso 1: fuzzificar cada entrada
    td  = fuzzificar(temp,   conjuntos.TEMP_MFS,  conjuntos.TEMP_U)
    tid = fuzzificar(tiempo, conjuntos.TIME_MFS,  conjuntos.TIME_U)
    thd = fuzzificar(grosor, conjuntos.THICK_MFS, conjuntos.THICK_U)

    # Paso 2 y 3: evaluar reglas y agregar por término de salida
    activaciones = {}  # {término: máxima activación alcanzada}
    resultados   = []  # registro de cada regla y su nivel de disparo

    for (t, ti, th, salida) in reglas:
        # AND difuso: la regla se activa al nivel del antecedente más débil
        act = min(td.get(t, 0), tid.get(ti, 0), thd.get(th, 0))
        resultados.append((t, ti, th, salida, act))

        # Si varias reglas apuntan al mismo término, gana la de mayor activación
        if salida not in activaciones or act > activaciones[salida]:
            activaciones[salida] = act

    # Paso 4: construir el área agregada recortando cada MF de salida
    agregado = np.zeros_like(conjuntos.TERM_U, dtype=float)
    for termino, fuerza in activaciones.items():
        if fuerza > 0:
            # fmin recorta la MF al nivel de activación; fmax une las áreas
            corte    = np.fmin(fuerza, conjuntos.TERM_MFS[termino])
            agregado = np.fmax(agregado, corte)

    # Paso 5: defuzzificación por centroide (centro de gravedad del área)
    try:
        if agregado.max() > 0:
            crisp = float(fuzz.defuzz(conjuntos.TERM_U, agregado, "centroid"))
        else:
            crisp = 0.0
    except Exception:
        crisp = 0.0

    return td, tid, thd, activaciones, resultados, agregado, crisp


# ─────────────────────────────────────────────────────────────────────────────
# INTERPRETACIÓN DEL RESULTADO
#
# Traduce el valor crisp (0–100) al término lingüístico correspondiente
# junto con su color representativo y una descripción para el usuario.
# ─────────────────────────────────────────────────────────────────────────────

def interpretar(crisp):
    if crisp < 12:
        return "Crudo",        "#8B0000", "Temperatura interna muy baja. No apta para consumo."
    elif crisp < 28:
        return "Azul",         "#D22B2B", "Interior casi crudo, muy rojo. ~49-55 C internos."
    elif crisp < 50:
        return "Medio",        "#E8503A", "Centro rosado y jugoso. ~60-66 C internos."
    elif crisp < 67:
        return "Tres Cuartos", "#C47840", "Ligeramente rosado al centro. ~66-72 C internos."
    elif crisp < 85:
        return "Bien Cocido",  "#8B4513", "Completamente cocida, sin rosa. ~77-82 C internos."
    else:
        return "Quemado",      "#1A0800", "Exceso de coccion. Carne carbonizada."
