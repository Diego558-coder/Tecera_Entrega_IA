from aplicacion import FuzzyApp

# ── Parámetros de entrada ──────────────────────────────────────────────────────
TEMPERATURA = 200    # °C   (0 – 300)
TIEMPO      = 10     # min  (0 – 120)
GROSOR      = 2.5    # cm   (0.0 – 6.0)
# ──────────────────────────────────────────────────────────────────────────────

app = FuzzyApp(temp=TEMPERATURA, tiempo=TIEMPO, grosor=GROSOR)
app.mainloop()
