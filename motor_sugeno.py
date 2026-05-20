import numpy as np
import conjuntos
import motor


# ─────────────────────────────────────────────────────────────────────────────
# INFERENCIA SUGENO (ORDEN CERO)
#
# Diferencia clave con Mamdani:
#   - El consecuente de cada regla NO es un conjunto difuso sino una
#     constante numérica k (definida en conjuntos.SUGENO_CONSTANTS).
#   - No se construye área agregada ni se aplica defuzzificación por centroide.
#   - El valor de salida es la media ponderada de las constantes:
#
#         y* = Σ(αᵢ · kᵢ) / Σ(αᵢ)
#
#   donde αᵢ es el nivel de activación de la regla i y kᵢ su constante.
#
# La fuzzificación y la evaluación AND de los antecedentes son idénticas
# a Mamdani (se reutiliza motor.fuzzificar).
# ─────────────────────────────────────────────────────────────────────────────

def inferir_sugeno(temp, tiempo, grosor, reglas=None):
    if reglas is None:
        reglas = conjuntos.RULES

    # Paso 1: fuzzificar entradas (igual que Mamdani)
    td  = motor.fuzzificar(temp,   conjuntos.TEMP_MFS,  conjuntos.TEMP_U)
    tid = motor.fuzzificar(tiempo, conjuntos.TIME_MFS,  conjuntos.TIME_U)
    thd = motor.fuzzificar(grosor, conjuntos.THICK_MFS, conjuntos.THICK_U)

    # Paso 2: evaluar reglas con AND = mínimo
    numerador   = 0.0
    denominador = 0.0
    activaciones = {}

    for (t, ti, th, salida) in reglas:
        act = min(td.get(t, 0), tid.get(ti, 0), thd.get(th, 0))
        if act > 0:
            k            = conjuntos.SUGENO_CONSTANTS[salida]
            numerador   += act * k
            denominador += act
            if salida not in activaciones or act > activaciones[salida]:
                activaciones[salida] = act

    # Paso 3: media ponderada (no hay defuzzificación)
    crisp = numerador / denominador if denominador > 0 else 0.0

    return td, tid, thd, activaciones, crisp
