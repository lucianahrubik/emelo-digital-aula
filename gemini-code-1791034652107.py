import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Gemelo Digital: Aula", layout="wide")
st.title("🌡️ Gemelo Digital: Simulación Térmica de un Aula")
st.markdown("Modifica los parámetros en la barra lateral para ver cómo evoluciona la temperatura del aula a lo largo del tiempo.")

# --- BARRA LATERAL (INPUTS) ---
st.sidebar.header("⚙️ Parámetros del Modelo")

t_simulacion = st.sidebar.slider("Tiempo de simulación (minutos)", 10, 120, 60)
t_inicial = st.sidebar.number_input("Temperatura Inicial del Aula (°C)", value=25.0, step=0.5)
t_exterior = st.sidebar.number_input("Temperatura Exterior (°C)", value=32.0, step=0.5)

st.sidebar.markdown("---")
st.sidebar.subheader("Cargas Térmicas")
num_alumnos = st.sidebar.slider("Cantidad de Alumnos", 0, 50, 30)
# Un aire de 3000 frigorías equivale a aprox 3.5 kW
ac_potencia = st.sidebar.selectbox("Potencia del Aire Acondicionado", 
                                   options=[0, 2500, 3000, 4500, 6000], 
                                   index=2,
                                   format_func=lambda x: f"Apagado" if x == 0 else f"{x} Frigorías")

estado_ac = st.sidebar.checkbox("Encender Aire Acondicionado", value=True)

# --- MODELO FÍSICO (Balance de Energía) ---
# Constantes simplificadas para un aula promedio (ej. 5x6x3 metros)
volumen_aula = 90.0 # m3
densidad_aire = 1.2 # kg/m3
calor_especifico_aire = 1005 # J/(kg·K)
masa_aire = volumen_aula * densidad_aire

# Factor de transferencia térmica de las paredes (simplificado)
coef_transferencia = 50.0 # W/°C 

# Calor emitido por persona (aprox 100 W = 100 J/s)
calor_por_alumno = 100.0 

# Conversión del AC (1 frigoría/h ≈ 1.163 W)
potencia_ac_watts = ac_potencia * 1.163 if estado_ac else 0

# --- SIMULACIÓN (Método de Euler) ---
dt = 60 # Paso de tiempo: 60 segundos (1 minuto)
temperaturas = [t_inicial]
tiempos = [0]

temp_actual = t_inicial

for minuto in range(1, t_simulacion + 1):
    # 1. Calor de los alumnos (calienta)
    Q_alumnos = num_alumnos * calor_por_alumno
    
    # 2. Transferencia con el exterior (calienta o enfría según delta T)
    Q_paredes = coef_transferencia * (t_exterior - temp_actual)
    
    # 3. Aire Acondicionado (enfría)
    Q_ac = -potencia_ac_watts
    
    # Balance total de energía en Watts (Joules/segundo)
    Q_total = Q_alumnos + Q_paredes + Q_ac
    
    # Cambio de temperatura en este minuto: dT = (Q * dt) / (m * Cp)
    delta_T = (Q_total * dt) / (masa_aire * calor_especifico_aire)
    temp_actual += delta_T
    
    tiempos.append(minuto)
    temperaturas.append(temp_actual)

# --- VISUALIZACIÓN ---
fig = go.Figure()

# Línea de temperatura del aula
fig.add_trace(go.Scatter(
    x=tiempos, y=temperaturas, 
    mode='lines', 
    name='Temp. Aula',
    line=dict(color='blue', width=3)
))

# Línea de referencia (Temperatura exterior)
fig.add_trace(go.Scatter(
    x=tiempos, y=[t_exterior]*(t_simulacion+1), 
    mode='lines', 
    name='Temp. Exterior',
    line=dict(color='red', width=2, dash='dash')
))

fig.update_layout(
    title="Evolución de la Temperatura",
    xaxis_title="Tiempo (minutos)",
    yaxis_title="Temperatura (°C)",
    yaxis=dict(range=[15, 40]),
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)

# --- MÉTRICAS FINALES ---
col1, col2 = st.columns(2)
col1.metric("Temperatura Final", f"{temperaturas[-1]:.1f} °C")
col2.metric("Estado del AC", "Encendido" if estado_ac else "Apagado")