# Streamlit Psychrometric App (SI units)
# Author: ChatGPT x Pablo
# Requirements: streamlit, psychrolib, numpy, matplotlib
# Run: streamlit run streamlit_psychrometric_app.py

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

try:
    import psychrolib
except Exception as e:
    raise SystemExit("PsychroLib is required. Install with: pip install psychrolib")

psychrolib.SetUnitSystem(psychrolib.SI)

# ---------------------------
# Helpers (thin wrappers)
# ---------------------------
GetHumRatioFromRelHum     = psychrolib.GetHumRatioFromRelHum
GetRelHumFromHumRatio     = psychrolib.GetRelHumFromHumRatio
GetHumRatioFromTWetBulb   = psychrolib.GetHumRatioFromTWetBulb
GetRelHumFromTWetBulb     = psychrolib.GetRelHumFromTWetBulb
GetTDewPointFromHumRatio  = psychrolib.GetTDewPointFromHumRatio
GetHumRatioFromTDewPoint  = psychrolib.GetHumRatioFromTDewPoint
GetVapPresFromRelHum      = psychrolib.GetVapPresFromRelHum
GetRelHumFromVapPres      = psychrolib.GetRelHumFromVapPres
GetSatVapPres             = psychrolib.GetSatVapPres
GetVapPresFromHumRatio    = psychrolib.GetVapPresFromHumRatio
GetMoistAirVolume         = psychrolib.GetMoistAirVolume
GetTWetBulbFromRelHum     = psychrolib.GetTWetBulbFromRelHum
GetTWetBulbFromHumRatio   = psychrolib.GetTWetBulbFromHumRatio

# ---------------------------
# UI
# ---------------------------
st.set_page_config(page_title="Psicrometría (SI)", page_icon="🌡️", layout="centered")
st.title("🌡️ Diagrama psicrométrico básico (SI)")
st.caption("App hermana de la de agua/vapor. Librería: PsychroLib (ASHRAE).")

with st.sidebar:
    st.header("Condiciones y entradas")
    P = st.number_input("Presión total P [Pa]", min_value=50_000.0, max_value=300_000.0, value=101_325.0, step=500.0, format="%0.1f")
    pair = st.radio(
        "Par de entrada",
        ["Tdb + RH", "Tdb + Twb", "Tdb + Tdp", "Tdb + W", "Tdb + Pv"],
        help="Elegí las dos variables conocidas para calcular el resto."
    )

    # Input fields depending on pair
    if pair == "Tdb + RH":
        Tdb = st.number_input("T bulbo seco Tdb [°C]", value=25.0, step=0.1, format="%0.2f")
        RH  = st.slider("Humedad relativa RH [%]", min_value=0.0, max_value=100.0, value=50.0, step=1.0) / 100.0
        Twb = None; Tdp=None; W=None; Pv=None
    elif pair == "Tdb + Twb":
        Tdb = st.number_input("T bulbo seco Tdb [°C]", value=30.0, step=0.1, format="%0.2f")
        Twb = st.number_input("T bulbo húmedo Twb [°C]", value=24.0, step=0.1, format="%0.2f")
        RH=None; Tdp=None; W=None; Pv=None
    elif pair == "Tdb + Tdp":
        Tdb = st.number_input("T bulbo seco Tdb [°C]", value=25.0, step=0.1, format="%0.2f")
        Tdp = st.number_input("T punto de rocío Tdp [°C]", value=13.0, step=0.1, format="%0.2f")
        RH=None; Twb=None; W=None; Pv=None
    elif pair == "Tdb + W":
        Tdb = st.number_input("T bulbo seco Tdb [°C]", value=25.0, step=0.1, format="%0.2f")
        W   = st.number_input("Humedad absoluta W [kg_vapor/kg_aire_seco]", min_value=0.0, value=0.010, step=0.001, format="%0.5f")
        RH=None; Twb=None; Tdp=None; Pv=None
    else:  # Tdb + Pv
        Tdb = st.number_input("T bulbo seco Tdb [°C]", value=25.0, step=0.1, format="%0.2f")
        Pv  = st.number_input("Presión parcial de vapor Pv [Pa]", min_value=0.0, value=2000.0, step=50.0, format="%0.1f")
        RH=None; Twb=None; Tdp=None; W=None

    # Rango de grafico
    st.subheader("Rango del gráfico")
    Tmin, Tmax = st.slider("Rango de Tdb [°C]", -10.0, 60.0, (0.0, 50.0), step=1.0)
    Wmax_gpkg = st.slider("Límite superior de W [g/kg aire seco]", 0.0, 40.0, 25.0, step=1.0)

# ---------------------------
# Cálculos principales
# ---------------------------
error = None
try:
    if pair == "Tdb + RH":
        W  = float(GetHumRatioFromRelHum(Tdb, RH, P))
        Pv = float(GetVapPresFromRelHum(Tdb, RH))
        Tdp = float(GetTDewPointFromHumRatio(Tdb, W, P))
        Twb = float(GetTWetBulbFromRelHum(Tdb, RH, P))
    elif pair == "Tdb + Twb":
        W  = float(GetHumRatioFromTWetBulb(Tdb, Twb, P))
        RH = float(GetRelHumFromTWetBulb(Tdb, Twb, P))
        Pv = float(GetVapPresFromHumRatio(W, P))
        Tdp = float(GetTDewPointFromHumRatio(Tdb, W, P))
    elif pair == "Tdb + Tdp":
        W  = float(GetHumRatioFromTDewPoint(Tdp, P))
        Pv = float(GetVapPresFromHumRatio(W, P))
        RH = float(GetRelHumFromHumRatio(Tdb, W, P))
        Twb = float(GetTWetBulbFromRelHum(Tdb, RH, P))
    elif pair == "Tdb + W":
        RH = float(GetRelHumFromHumRatio(Tdb, W, P))
        Pv = float(GetVapPresFromHumRatio(W, P))
        Tdp = float(GetTDewPointFromHumRatio(Tdb, W, P))
        Twb = float(GetTWetBulbFromHumRatio(Tdb, W, P))
    elif pair == "Tdb + Pv":
        RH = float(GetRelHumFromVapPres(Tdb, Pv))
        W  = float(GetHumRatioFromRelHum(Tdb, RH, P))
        Tdp = float(GetTDewPointFromHumRatio(Tdb, W, P))
        Twb = float(GetTWetBulbFromRelHum(Tdb, RH, P))
    else:
        error = "Par de entrada no reconocido."

    Pws = float(GetSatVapPres(Tdb))  # Presión de vapor saturado a Tdb
    v   = float(GetMoistAirVolume(Tdb, W, P))  # m3/kg aire seco

except Exception as e:
    error = f"Error en el cálculo: {e}"

# ---------------------------
# Salidas numéricas
# ---------------------------
st.subheader("Resultados (SI)")

if error:
    st.error(error)
else:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("T bulbo seco Tdb", f"{Tdb:.2f} °C")
        st.metric("Humedad relativa RH", f"{RH*100:.1f} %")
        st.metric("P total", f"{P:,.0f} Pa")
    with col2:
        st.metric("Humedad absoluta W", f"{W:.5f} kg/kg_da")
        st.metric("W", f"{W*1000:.2f} g/kg_da")
        st.metric("Volumen específico v", f"{v:.4f} m³/kg_da")
    with col3:
        st.metric("T bulbo húmedo Twb", f"{Twb:.2f} °C")
        st.metric("T punto de rocío Tdp", f"{Tdp:.2f} °C")
        st.metric("P vapor Pv", f"{Pv:,.1f} Pa")
        st.caption(f"P vapor saturado a Tdb: {Pws:,.1f} Pa")

# ---------------------------
# Gráfico psicrométrico básico
# ---------------------------
if not error:
    fig, ax = plt.subplots(figsize=(7, 5), dpi=120)

    # Curva de saturación (RH = 100%)
    Ts = np.linspace(Tmin, Tmax, 200)
    Ws = np.array([GetHumRatioFromRelHum(T, 1.0, P) for T in Ts])

    ax.plot(Ts, Ws*1000, linewidth=2, label="ϕ = 100% (saturación)")

    # Punto calculado
    ax.scatter([Tdb], [W*1000], s=60, marker='o', label="Punto")

    # Etiquetas
    ax.set_xlabel("Temperatura bulbo seco Tdb [°C]")
    ax.set_ylabel("Humedad absoluta W [g/kg aire seco]")
    ax.set_xlim(Tmin, Tmax)
    ax.set_ylim(0, Wmax_gpkg)
    ax.grid(True, which='both', alpha=0.3)
    ax.legend(loc='best')

    st.pyplot(fig)

# ---------------------------
# Notas
# ---------------------------
st.markdown(
    """
**Notas:**
- Ecuaciones de *PsychroLib* (ASHRAE). Unidades SI.
- "W" es la relación de humedad en **kg de vapor / kg de aire seco**.
- El volumen específico se reporta en **m³/kg de aire seco**.
- La curva mostrada es únicamente ϕ = 100% (saturación). Se pueden agregar isohumedades relativas en futuras versiones.
    """
)
