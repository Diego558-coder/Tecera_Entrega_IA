import numpy as np
import skfuzzy as fuzz

# ─────────────────────────────────────────────────────────────────────────────
# UNIVERSOS DE DISCURSO
# Cada universo define el rango de valores posibles para cada variable.
# Son arreglos de numpy que sirven como eje X de las funciones de membresía.
# ─────────────────────────────────────────────────────────────────────────────

TEMP_U  = np.arange(0, 301, 1)      # Temperatura del horno: 0 a 300 °C
TIME_U  = np.arange(0, 121, 1)      # Tiempo de cocción: 0 a 120 minutos
THICK_U = np.linspace(0, 6, 300)    # Grosor de la carne: 0 a 6 cm
TERM_U  = np.arange(0, 101, 1)      # Término de cocción (salida): 0 a 100

# ─────────────────────────────────────────────────────────────────────────────
# FUNCIONES DE MEMBRESÍA — ENTRADAS
#
# Usamos funciones trapezoidales (trapmf) definidas por 4 puntos [a, b, c, d]:
#   - De 0 a 'a': membresía = 0
#   - De 'a' a 'b': sube de 0 a 1
#   - De 'b' a 'c': membresía = 1 (parte plana)
#   - De 'c' a 'd': baja de 1 a 0
#   - De 'd' en adelante: membresía = 0
# Los extremos comparten valores iguales para "abrir" el trapecio hacia afuera.
# ─────────────────────────────────────────────────────────────────────────────

# Conjuntos para la temperatura del horno (°C)
TEMP_MFS = {
    "Baja":     fuzz.trapmf(TEMP_U, [0,   0,   80,  140]),
    "Media":    fuzz.trapmf(TEMP_U, [100, 150, 180, 220]),
    "Alta":     fuzz.trapmf(TEMP_U, [180, 210, 240, 270]),
    "Muy Alta": fuzz.trapmf(TEMP_U, [240, 265, 300, 300]),
}

# Conjuntos para el tiempo de cocción (minutos)
TIME_MFS = {
    "Poco":     fuzz.trapmf(TIME_U, [0,   0,   20,  40]),
    "Moderado": fuzz.trapmf(TIME_U, [25,  40,  55,  70]),
    "Mucho":    fuzz.trapmf(TIME_U, [55,  70,  85,  100]),
    "Excesivo": fuzz.trapmf(TIME_U, [85,  100, 120, 120]),
}

# Conjuntos para el grosor de la carne (cm)
THICK_MFS = {
    "Delgada":    fuzz.trapmf(THICK_U, [0.0, 0.0, 1.0, 2.0]),
    "Normal":     fuzz.trapmf(THICK_U, [1.5, 2.0, 2.8, 3.5]),
    "Gruesa":     fuzz.trapmf(THICK_U, [3.0, 3.5, 4.5, 5.0]),
    "Muy Gruesa": fuzz.trapmf(THICK_U, [4.5, 5.0, 6.0, 6.0]),
}

# ─────────────────────────────────────────────────────────────────────────────
# FUNCIONES DE MEMBRESÍA — SALIDA
#
# La variable de salida representa el "término" de cocción en una escala 0-100.
# Valores bajos = cruda, valores altos = quemada.
# ─────────────────────────────────────────────────────────────────────────────

TERM_MFS = {
    "Crudo":        fuzz.trapmf(TERM_U, [0,  0,  8,  15]),
    "Azul":         fuzz.trapmf(TERM_U, [10, 18, 25, 32]),
    "Medio":        fuzz.trapmf(TERM_U, [28, 38, 48, 58]),
    "Tres Cuartos": fuzz.trapmf(TERM_U, [50, 58, 65, 73]),
    "Bien Cocido":  fuzz.trapmf(TERM_U, [68, 75, 82, 88]),
    "Quemado":      fuzz.trapmf(TERM_U, [83, 90, 100, 100]),
}

# Colores para graficar cada conjunto de la salida
TERM_COLORS = {
    "Crudo":        "#8B0000",
    "Azul":         "#D22B2B",
    "Medio":        "#E8503A",
    "Tres Cuartos": "#C47840",
    "Bien Cocido":  "#8B4513",
    "Quemado":      "#1A0800",
}

# Colores para graficar las entradas
TEMP_COLORS  = ["#5599EE", "#55CCEE", "#EEAA22", "#EE3322"]
TIME_COLORS  = ["#55AA44", "#44BBAA", "#BBBB00", "#BB5500"]
THICK_COLORS = ["#AA77CC", "#CC44BB", "#BB5577", "#993399"]

# ─────────────────────────────────────────────────────────────────────────────
# BASE DE REGLAS (64 reglas = 4 temperaturas × 4 tiempos × 4 grosores)
#
# Cada regla tiene la forma:
#   SI (Temperatura es X) Y (Tiempo es Y) Y (Grosor es Z) ENTONCES (Término es T)
#
# El conector Y se evalúa con el operador mínimo (lógica difusa de Mamdani).
# ─────────────────────────────────────────────────────────────────────────────

RULES = [
    # ── Temperatura BAJA (~80-140 C) ─────────────────────────────────────────
    # Ref: low-and-slow 250F (121C) → Medium-Rare en 20-25 min (USDA / McGee)
    # El calor suave penetra lento; tiempos cortos dejan el interior crudo.
    ("Baja",     "Poco",     "Delgada",    "Crudo"),
    ("Baja",     "Poco",     "Normal",     "Crudo"),
    ("Baja",     "Poco",     "Gruesa",     "Crudo"),
    ("Baja",     "Poco",     "Muy Gruesa", "Crudo"),
    ("Baja",     "Moderado", "Delgada",    "Azul"),
    ("Baja",     "Moderado", "Normal",     "Azul"),         # 25-55 min, 121C, 2.5cm → Rare
    ("Baja",     "Moderado", "Gruesa",     "Crudo"),
    ("Baja",     "Moderado", "Muy Gruesa", "Crudo"),
    ("Baja",     "Mucho",    "Delgada",    "Medio"),
    ("Baja",     "Mucho",    "Normal",     "Azul"),
    ("Baja",     "Mucho",    "Gruesa",     "Azul"),         # 55-90 min, 121C, 3.8cm → algo de coccion
    ("Baja",     "Mucho",    "Muy Gruesa", "Crudo"),
    ("Baja",     "Excesivo", "Delgada",    "Tres Cuartos"),
    ("Baja",     "Excesivo", "Normal",     "Tres Cuartos"), # 90+ min, 121C, 2.5cm → Med-Well
    ("Baja",     "Excesivo", "Gruesa",     "Medio"),        # 90+ min, 121C, 3.8cm → Medium
    ("Baja",     "Excesivo", "Muy Gruesa", "Azul"),         # 90+ min, 121C, 5cm → algo de coccion

    # ── Temperatura MEDIA (~150-220 C) ────────────────────────────────────────
    # Horno estandar. Tiempos moderados → terminos medios segun grosor.
    ("Media",    "Poco",     "Delgada",    "Azul"),
    ("Media",    "Poco",     "Normal",     "Crudo"),
    ("Media",    "Poco",     "Gruesa",     "Crudo"),
    ("Media",    "Poco",     "Muy Gruesa", "Crudo"),
    ("Media",    "Moderado", "Delgada",    "Medio"),
    ("Media",    "Moderado", "Normal",     "Medio"),        # 25-55 min, 165C, 2.5cm → Medium
    ("Media",    "Moderado", "Gruesa",     "Azul"),         # 25-55 min, 165C, 3.8cm → Rare
    ("Media",    "Moderado", "Muy Gruesa", "Crudo"),
    ("Media",    "Mucho",    "Delgada",    "Tres Cuartos"),
    ("Media",    "Mucho",    "Normal",     "Tres Cuartos"), # 55-90 min, 165C, 2.5cm → Med-Well
    ("Media",    "Mucho",    "Gruesa",     "Medio"),        # 55-90 min, 165C, 3.8cm → Medium
    ("Media",    "Mucho",    "Muy Gruesa", "Azul"),         # 55-90 min, 165C, 5cm → Rare
    ("Media",    "Excesivo", "Delgada",    "Quemado"),      # 90+ min, 165C, delgada → quemada
    ("Media",    "Excesivo", "Normal",     "Bien Cocido"),  # 90+ min, 165C, 2.5cm → Well Done
    ("Media",    "Excesivo", "Gruesa",     "Tres Cuartos"), # 90+ min, 165C, 3.8cm → Med-Well
    ("Media",    "Excesivo", "Muy Gruesa", "Medio"),        # 90+ min, 165C, 5cm → Medium

    # ── Temperatura ALTA (~180-270 C / 425F) ──────────────────────────────────
    # Ref: oven bake 425F → 1" (2.5cm): Rare 5-7min, Medium 11-13min, MedWell 13-15min
    ("Alta",     "Poco",     "Delgada",    "Medio"),        # 5-20 min, 218C, <2cm → Medium
    ("Alta",     "Poco",     "Normal",     "Azul"),         # 5-10 min, 218C, 2.5cm → Rare/MedRare
    ("Alta",     "Poco",     "Gruesa",     "Crudo"),
    ("Alta",     "Poco",     "Muy Gruesa", "Crudo"),
    ("Alta",     "Moderado", "Delgada",    "Bien Cocido"),  # 25-55 min, 218C, delgada → Well Done
    ("Alta",     "Moderado", "Normal",     "Tres Cuartos"), # 25-55 min, 218C, 2.5cm → Med-Well
    ("Alta",     "Moderado", "Gruesa",     "Medio"),        # 25-55 min, 218C, 3.8cm → Medium
    ("Alta",     "Moderado", "Muy Gruesa", "Azul"),         # 25-55 min, 218C, 5cm → Rare
    ("Alta",     "Mucho",    "Delgada",    "Quemado"),      # 55+ min, 218C, delgada → quemada
    ("Alta",     "Mucho",    "Normal",     "Quemado"),      # 55+ min, 218C, 2.5cm → quemado
    ("Alta",     "Mucho",    "Gruesa",     "Bien Cocido"),  # 55+ min, 218C, 3.8cm → Well Done
    ("Alta",     "Mucho",    "Muy Gruesa", "Tres Cuartos"), # 55+ min, 218C, 5cm → Med-Well
    ("Alta",     "Excesivo", "Delgada",    "Quemado"),
    ("Alta",     "Excesivo", "Normal",     "Quemado"),      # 90+ min, 218C, 2.5cm → quemado
    ("Alta",     "Excesivo", "Gruesa",     "Quemado"),      # 90+ min, 218C, 3.8cm → quemado
    ("Alta",     "Excesivo", "Muy Gruesa", "Bien Cocido"),  # 90+ min, 218C, 5cm → Well Done

    # ── Temperatura MUY ALTA (~240-300 C) ─────────────────────────────────────
    # Calor muy agresivo: lo que Alta hace en Moderado, Muy Alta lo hace en Poco.
    ("Muy Alta", "Poco",     "Delgada",    "Bien Cocido"),  # alta T + delgada → Well Done rapido
    ("Muy Alta", "Poco",     "Normal",     "Medio"),
    ("Muy Alta", "Poco",     "Gruesa",     "Azul"),
    ("Muy Alta", "Poco",     "Muy Gruesa", "Crudo"),
    ("Muy Alta", "Moderado", "Delgada",    "Quemado"),      # 25+ min a 270C, delgada → quemado
    ("Muy Alta", "Moderado", "Normal",     "Quemado"),      # 25+ min a 270C, 2.5cm → quemado
    ("Muy Alta", "Moderado", "Gruesa",     "Bien Cocido"),  # 25+ min a 270C, 3.8cm → Well Done
    ("Muy Alta", "Moderado", "Muy Gruesa", "Tres Cuartos"), # 25+ min a 270C, 5cm → Med-Well
    ("Muy Alta", "Mucho",    "Delgada",    "Quemado"),
    ("Muy Alta", "Mucho",    "Normal",     "Quemado"),      # 55+ min a 270C, 2.5cm → quemado
    ("Muy Alta", "Mucho",    "Gruesa",     "Quemado"),      # 55+ min a 270C, 3.8cm → quemado
    ("Muy Alta", "Mucho",    "Muy Gruesa", "Bien Cocido"),  # 55+ min a 270C, 5cm → Well Done
    ("Muy Alta", "Excesivo", "Delgada",    "Quemado"),
    ("Muy Alta", "Excesivo", "Normal",     "Quemado"),
    ("Muy Alta", "Excesivo", "Gruesa",     "Quemado"),      # 90+ min a 270C → quemado
    ("Muy Alta", "Excesivo", "Muy Gruesa", "Quemado"),      # 90+ min a 270C → quemado
]
