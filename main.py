from aplicacion import FuzzyApp

# ── Parámetros de entrada ──────────────────────────────────────────────────────
TEMPERATURA = 125    # °C   (0 – 300)
TIEMPO      = 90     # min  (0 – 120)
GROSOR      = 3.25    # cm   (0.0 – 6.0)
# ──────────────────────────────────────────────────────────────────────────────

app = FuzzyApp(temp=TEMPERATURA, tiempo=TIEMPO, grosor=GROSOR)
app.mainloop()
