import numpy as np
import skfuzzy as fuzz

# Universos de discurso
TEMP_U  = np.arange(0, 301, 1)
TIME_U  = np.arange(0, 121, 1)
THICK_U = np.linspace(0, 6, 300)
TERM_U  = np.arange(0, 101, 1)

# Funciones de membresia - entradas
TEMP_MFS = {
    "Baja":     fuzz.trapmf(TEMP_U, [0,   0,   80,  140]),
    "Media":    fuzz.trapmf(TEMP_U, [100, 150, 180, 220]),
    "Alta":     fuzz.trapmf(TEMP_U, [180, 210, 240, 270]),
    "Muy Alta": fuzz.trapmf(TEMP_U, [240, 265, 300, 300]),
}
TIME_MFS = {
    "Poco":     fuzz.trapmf(TIME_U, [0,   0,   20,  40]),
    "Moderado": fuzz.trapmf(TIME_U, [25,  40,  55,  70]),
    "Mucho":    fuzz.trapmf(TIME_U, [55,  70,  85,  100]),
    "Excesivo": fuzz.trapmf(TIME_U, [85,  100, 120, 120]),
}
THICK_MFS = {
    "Delgada":    fuzz.trapmf(THICK_U, [0.0, 0.0, 1.0, 2.0]),
    "Normal":     fuzz.trapmf(THICK_U, [1.5, 2.0, 2.8, 3.5]),
    "Gruesa":     fuzz.trapmf(THICK_U, [3.0, 3.5, 4.5, 5.0]),
    "Muy Gruesa": fuzz.trapmf(THICK_U, [4.5, 5.0, 6.0, 6.0]),
}

# Funciones de membresia - salida
TERM_MFS = {
    "Crudo":        fuzz.trapmf(TERM_U, [0,  0,  8,  15]),
    "Azul":         fuzz.trapmf(TERM_U, [10, 18, 25, 32]),
    "Medio":        fuzz.trapmf(TERM_U, [28, 38, 48, 58]),
    "Tres Cuartos": fuzz.trapmf(TERM_U, [50, 58, 65, 73]),
    "Bien Cocido":  fuzz.trapmf(TERM_U, [68, 75, 82, 88]),
    "Quemado":      fuzz.trapmf(TERM_U, [83, 90, 100, 100]),
}

# Colores por conjunto
TERM_COLORS  = {
    "Crudo":        "#8B0000",
    "Azul":         "#D22B2B",
    "Medio":        "#E8503A",
    "Tres Cuartos": "#C47840",
    "Bien Cocido":  "#8B4513",
    "Quemado":      "#1A0800",
}
TEMP_COLORS  = ["#5599EE", "#55CCEE", "#EEAA22", "#EE3322"]
TIME_COLORS  = ["#55AA44", "#44BBAA", "#BBBB00", "#BB5500"]
THICK_COLORS = ["#AA77CC", "#CC44BB", "#BB5577", "#993399"]

# 64 reglas: (Temperatura, Tiempo, Grosor) -> Termino
RULES = [
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
