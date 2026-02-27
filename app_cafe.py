import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(page_title="Painel do Café 2026", layout="wide")

st.title("☕ Painel de Análise: Arábica vs Conilon")
st.markdown("Análise de tendências e previsão baseada em médias móveis (MA20).")

# Sidebar para escolha do café
cafe_tipo = st.sidebar.selectbox("Escolha o tipo de Café", ["Arábica (NY)", "Conilon (Londres)"])
ticker = "KC=F" if cafe_tipo == "Arábica (NY)" else "RC=F"

# Função para buscar e limpar dados
def buscar_dados(ticker_code):
    data = yf.download(ticker_code, period="6mo", interval="1d")
    # Limpeza para evitar o erro MultiIndex (ValueError)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    return data

df = buscar_dados(ticker)

if not df.empty:
    # Tratamento de valores para garantir que sejam floats simples
    preco_atual = float(df['Close'].iloc[-1])
    preco_anterior = float(df['Close'].iloc[-2])
    variacao = preco_atual - preco_anterior
    
    # Cálculo da Média Móvel de 20 dias
    df['MA20'] = df['Close'].rolling(window=20).mean()
    media_atual = float(df['MA20'].iloc[-1])
    
    # Lógica de Tendência
    if preco_atual > media_atual:
        tendencia = "Subida 📈"
        cor_tendencia = "green"
        msg = f"O mercado está em ALTA. O preço de {preco_atual:.2f} está acima da média de 20 dias ({media_atual:.2f})."
    else:
        tendencia = "Baixa 📉"
        cor_tendencia = "red"
        msg = f"O mercado está em BAIXA. O preço de {preco_atual:.2f} está abaixo da média de 20 dias ({media_atual:.2f})."

    # Exibição de Métricas
    col1, col2, col3 = st.columns(3)
    col1.metric("Preço Atual (USD)", f"{preco_atual:.2f}")
    col2.metric("Variação Diária", f"{variacao:.2f}")
    col3.subheader(f"Tendência: {tendencia}")

    # Gráfico Interativo
    fig = go.Figure()
    # Velas (Candlestick)
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], 
                                 low=df['Low'], close=df['Close'], name="Preço Mercado"))
    # Linha da Média Móvel
    fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], name="Média 20 dias", line=dict(color='orange', width=2)))
    
    fig.update_layout(title=f"Histórico de Preços - {cafe_tipo}", yaxis_title="Preço (USD)", xaxis_title="Data")
    st.plotly_chart(fig, use_container_width=True)

    # Painel de Previsão
    st.info(f"**Análise do Especialista IA:** {msg}")
    
    st.divider()
    st.caption("Nota: O Café Arábica é cotado em centavos de dólar por libra-peso em NY. O Conilon é cotado em dólares por tonelada em Londres.")

else:
    st.error("Não foi possível carregar os dados. Tente novamente mais tarde.")
