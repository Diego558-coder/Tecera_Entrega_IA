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
    # Temperatura BAJA
    ("Baja",     "Poco",     "Delgada",    "Crudo"),
    ("Baja",     "Poco",     "Normal",     "Crudo"),
    ("Baja",     "Poco",     "Gruesa",     "Crudo"),
    ("Baja",     "Poco",     "Muy Gruesa", "Crudo"),
    ("Baja",     "Moderado", "Delgada",    "Azul"),
    ("Baja",     "Moderado", "Normal",     "Crudo"),
    ("Baja",     "Moderado", "Gruesa",     "Crudo"),
    ("Baja",     "Moderado", "Muy Gruesa", "Crudo"),
    ("Baja",     "Mucho",    "Delgada",    "Medio"),
    ("Baja",     "Mucho",    "Normal",     "Azul"),
    ("Baja",     "Mucho",    "Gruesa",     "Crudo"),
    ("Baja",     "Mucho",    "Muy Gruesa", "Crudo"),
    ("Baja",     "Excesivo", "Delgada",    "Tres Cuartos"),
    ("Baja",     "Excesivo", "Normal",     "Medio"),
    ("Baja",     "Excesivo", "Gruesa",     "Azul"),
    ("Baja",     "Excesivo", "Muy Gruesa", "Crudo"),
    # Temperatura MEDIA
    ("Media",    "Poco",     "Delgada",    "Azul"),
    ("Media",    "Poco",     "Normal",     "Crudo"),
    ("Media",    "Poco",     "Gruesa",     "Crudo"),
    ("Media",    "Poco",     "Muy Gruesa", "Crudo"),
    ("Media",    "Moderado", "Delgada",    "Medio"),
    ("Media",    "Moderado", "Normal",     "Azul"),
    ("Media",    "Moderado", "Gruesa",     "Crudo"),
    ("Media",    "Moderado", "Muy Gruesa", "Crudo"),
    ("Media",    "Mucho",    "Delgada",    "Tres Cuartos"),
    ("Media",    "Mucho",    "Normal",     "Medio"),
    ("Media",    "Mucho",    "Gruesa",     "Azul"),
    ("Media",    "Mucho",    "Muy Gruesa", "Crudo"),
    ("Media",    "Excesivo", "Delgada",    "Bien Cocido"),
    ("Media",    "Excesivo", "Normal",     "Tres Cuartos"),
    ("Media",    "Excesivo", "Gruesa",     "Medio"),
    ("Media",    "Excesivo", "Muy Gruesa", "Azul"),
    # Temperatura ALTA
    ("Alta",     "Poco",     "Delgada",    "Medio"),
    ("Alta",     "Poco",     "Normal",     "Azul"),
    ("Alta",     "Poco",     "Gruesa",     "Crudo"),
    ("Alta",     "Poco",     "Muy Gruesa", "Crudo"),
    ("Alta",     "Moderado", "Delgada",    "Tres Cuartos"),
    ("Alta",     "Moderado", "Normal",     "Medio"),
    ("Alta",     "Moderado", "Gruesa",     "Azul"),
    ("Alta",     "Moderado", "Muy Gruesa", "Crudo"),
    ("Alta",     "Mucho",    "Delgada",    "Bien Cocido"),
    ("Alta",     "Mucho",    "Normal",     "Tres Cuartos"),
    ("Alta",     "Mucho",    "Gruesa",     "Medio"),
    ("Alta",     "Mucho",    "Muy Gruesa", "Azul"),
    ("Alta",     "Excesivo", "Delgada",    "Quemado"),
    ("Alta",     "Excesivo", "Normal",     "Bien Cocido"),
    ("Alta",     "Excesivo", "Gruesa",     "Tres Cuartos"),
    ("Alta",     "Excesivo", "Muy Gruesa", "Medio"),
    # Temperatura MUY ALTA
    ("Muy Alta", "Poco",     "Delgada",    "Tres Cuartos"),
    ("Muy Alta", "Poco",     "Normal",     "Medio"),
    ("Muy Alta", "Poco",     "Gruesa",     "Azul"),
    ("Muy Alta", "Poco",     "Muy Gruesa", "Crudo"),
    ("Muy Alta", "Moderado", "Delgada",    "Bien Cocido"),
    ("Muy Alta", "Moderado", "Normal",     "Tres Cuartos"),
    ("Muy Alta", "Moderado", "Gruesa",     "Medio"),
    ("Muy Alta", "Moderado", "Muy Gruesa", "Azul"),
    ("Muy Alta", "Mucho",    "Delgada",    "Quemado"),
    ("Muy Alta", "Mucho",    "Normal",     "Bien Cocido"),
    ("Muy Alta", "Mucho",    "Gruesa",     "Tres Cuartos"),
    ("Muy Alta", "Mucho",    "Muy Gruesa", "Medio"),
    ("Muy Alta", "Excesivo", "Delgada",    "Quemado"),
    ("Muy Alta", "Excesivo", "Normal",     "Quemado"),
    ("Muy Alta", "Excesivo", "Gruesa",     "Bien Cocido"),
    ("Muy Alta", "Excesivo", "Muy Gruesa", "Tres Cuartos"),
]
