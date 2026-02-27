import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Configuração da página
st.set_page_config(page_title="Painel do Café 2026", layout="wide")

st.title("☕ Painel de Análise: Arábica vs Conilon")
st.markdown("Análise de tendências e previsão baseada em médias móveis.")

# Função para buscar dados
def buscar_dados(ticker, periodo="6mo"):
    data = yf.download(ticker, period=periodo, interval="1d")
    return data

# Sidebar para escolha do café
cafe_tipo = st.sidebar.selectbox("Escolha o tipo de Café", ["Arábica (NY)", "Conilon/Robusta (Londres)"])
ticker = "KC=F" if cafe_tipo == "Arábica (NY)" else "RC=F"

# Obtendo os dados
df = buscar_dados(ticker)

if not df.empty:
    # Cálculos de Indicadores
    preco_atual = df['Close'].iloc[-1]
    preco_anterior = df['Close'].iloc[-2]
    variacao = preco_atual - preco_anterior
    
    # Média Móvel Simples (Trend)
    df['MA20'] = df['Close'].rolling(window=20).mean()
    tendencia = "Subida 📈" if preco_atual > df['MA20'].iloc[-1] else "Baixa 📉"
    
    # Layout de métricas
    col1, col2, col3 = st.columns(3)
    col1.metric("Preço Atual (USD)", f"{preco_atual:.2f}")
    col2.metric("Variação Diária", f"{variacao:.2f}", delta_color="normal")
    col3.metric("Tendência (Base MA20)", tendencia)

    # Gráfico
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], 
                                 low=df['Low'], close=df['Close'], name="Preço"))
    fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], name="Média 20 dias", line=dict(color='orange')))
    
    st.plotly_chart(fig, use_container_width=True)

    # Lógica de Análise Simples
    st.subheader("Análise de Mercado")
    if tendencia == "Subida 📈":
        st.success(f"O {cafe_tipo} está em tendência de alta. O suporte atual está em torno de {df['MA20'].iloc[-1]:.2f}.")
    else:
        st.error(f"O {cafe_tipo} está em tendência de baixa. Pode cair mais até encontrar novo suporte.")
else:
    st.error("Erro ao carregar dados. Verifique a conexão ou o ticker.")
