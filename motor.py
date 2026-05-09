import numpy as np
import skfuzzy as fuzz
import conjuntos


class MotorDifuso:
    """Realiza la inferencia Mamdani completa:
    fuzzificacion, evaluacion de reglas, agregacion y defuzzificacion."""

    def __init__(self):
        self.temp_mfs  = conjuntos.TEMP_MFS
        self.time_mfs  = conjuntos.TIME_MFS
        self.thick_mfs = conjuntos.THICK_MFS
        self.term_mfs  = conjuntos.TERM_MFS
        self.reglas    = conjuntos.RULES

    @staticmethod
    def fuzzificar(valor, mf_dict, universo):
        v = float(np.clip(valor, universo[0], universo[-1]))
        return {nombre: float(fuzz.interp_membership(universo, mf, v))
                for nombre, mf in mf_dict.items()}

    def inferir(self, temp, tiempo, grosor):
        td  = self.fuzzificar(temp,   self.temp_mfs,  conjuntos.TEMP_U)
        tid = self.fuzzificar(tiempo, self.time_mfs,  conjuntos.TIME_U)
        thd = self.fuzzificar(grosor, self.thick_mfs, conjuntos.THICK_U)

        activaciones = {}
        resultados   = []
        for (t, ti, th, salida) in self.reglas:
            act = min(td.get(t, 0), tid.get(ti, 0), thd.get(th, 0))
            resultados.append((t, ti, th, salida, act))
            activaciones[salida] = max(activaciones.get(salida, 0), act)

        agregado = np.zeros_like(conjuntos.TERM_U, dtype=float)
        for termino, fuerza in activaciones.items():
            if fuerza > 0:
                agregado = np.fmax(agregado,
                                   np.fmin(fuerza, self.term_mfs[termino]))

        try:
            crisp = (float(fuzz.defuzz(conjuntos.TERM_U, agregado, "centroid"))
                     if agregado.max() > 0 else 0.0)
        except Exception:
            crisp = 0.0

        return td, tid, thd, activaciones, resultados, agregado, crisp

    @staticmethod
    def interpretar(crisp):
        tabla = [
            (12,  "Crudo",        "#8B0000", "Temperatura interna muy baja. No apta para consumo."),
            (28,  "Azul",         "#D22B2B", "Interior casi crudo, muy rojo. ~49-55 C internos."),
            (50,  "Medio",        "#E8503A", "Centro rosado y jugoso. ~60-66 C internos."),
            (67,  "Tres Cuartos", "#C47840", "Ligeramente rosado al centro. ~66-72 C internos."),
            (85,  "Bien Cocido",  "#8B4513", "Completamente cocida, sin rosa. ~77-82 C internos."),
            (101, "Quemado",      "#1A0800", "Exceso de coccion. Carne carbonizada."),
        ]
        for umbral, nombre, color, desc in tabla:
            if crisp < umbral:
                return nombre, color, desc
        return "Quemado", "#1A0800", "Exceso de coccion."
