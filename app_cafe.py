import streamlit as st
import pandas as pd
import yfinance as yf
import requests

# Configuração da página
st.set_page_config(page_title="Previsão Café ES", page_icon="☕", layout="wide")

# --- FUNÇÃO MELHORADA PARA O CCCV ---
def buscar_dados_cccv():
    url = "https://www.cccv.org.br/cotacao/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        tabelas = pd.read_html(response.text)
        df = tabelas[0]
        
        # Busca os valores (Dura e Rio)
        dura_str = df.loc[df[0].str.contains("dura", case=False), 1].values[0]
        rio_str = df.loc[df[0].str.contains("rio", case=False), 1].values[0]
        
        dura = float(dura_str.replace('.', '').replace(',', '.'))
        rio = float(rio_str.replace('.', '').replace(',', '.'))
        return dura, rio
    except Exception as e:
        # Se o site falhar, usamos valores de referência para o app não travar
        return 1694.00, 1349.00 

# --- FUNÇÃO PARA MERCADO FINANCEIRO ---
def buscar_mercado_financeiro():
    try:
        # Puxamos 5 dias para garantir que sempre tenha dados, mesmo em feriados
        cafe_ny = yf.download("KC=F", period="5d", interval="1d")
        dolar = yf.download("USDBRL=X", period="5d", interval="1d")
        
        cotacao_ny = cafe_ny['Close'].iloc[-1]
        var_ny = (cafe_ny['Close'].iloc[-1] / cafe_ny['Close'].iloc[-2]) - 1
        
        cotacao_usd = dolar['Close'].iloc[-1]
        var_usd = (dolar['Close'].iloc[-1] / dolar['Close'].iloc[-2]) - 1
        
        return float(cotacao_ny), float(var_ny), float(cotacao_usd), float(var_usd)
    except:
        return 0.0, 0.0, 0.0, 0.0

# --- INTERFACE DO SITE ---
st.title("📊 Monitor de Tendência do Café - Espírito Santo")

preco_dura_base, preco_rio_base = buscar_dados_cccv()
cot_ny, v_ny, cot_usd, v_usd = buscar_mercado_financeiro()

if cot_ny == 0:
    st.warning("Aguardando abertura do mercado financeiro...")
else:
    variacao_total = v_ny + v_usd

    col1, col2, col3 = st.columns(3)
    col1.metric("Bolsa NY (Arábica)", f"{cot_ny:.2f} pts", f"{v_ny:.2%}")
    col2.metric("Dólar Comercial", f"R$ {cot_usd:.2f}", f"{v_usd:.2%}")
    col3.metric("Tendência Total", f"{(variacao_total*100):.2f}%")

    st.divider()

    col_dura, col_rio = st.columns(2)

    # Cálculo Dura
    mudanca_dura = preco_dura_base * variacao_total
    with col_dura:
        st.subheader("☕ Bebida DURA")
        st.metric("Alvo Estimado", f"R$ {preco_dura_base + mudanca_dura:.2f}", f"R$ {mudanca_dura:.2f}")

    # Cálculo Rio
    mudanca_rio = preco_rio_base * variacao_total
    with col_rio:
        st.subheader("☕ Bebida RIO")
        st.metric("Alvo Estimado", f"R$ {preco_rio_base + mudanca_rio:.2f}", f"R$ {mudanca_rio:.2f}")
