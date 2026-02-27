import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import base64
import os

# --- 1. PRIMEIRO AS FUNÇÕES (Para evitar o erro NameError) ---
def buscar_dados_cccv():
    url = "https://www.cccv.org.br/cotacao/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        tabelas = pd.read_html(response.text)
        df = tabelas[0]
        dura_str = df.loc[df[0].str.contains("dura", case=False), 1].values[0]
        rio_str = df.loc[df[0].str.contains("rio", case=False), 1].values[0]
        dura = float(str(dura_str).replace('.', '').replace(',', '.'))
        rio = float(str(rio_str).replace('.', '').replace(',', '.'))
        return dura, rio
    except:
        return 1694.00, 1349.00

def buscar_mercado():
    try:
        ticker_ny = yf.Ticker("KC=F")
        ticker_usd = yf.Ticker("USDBRL=X")
        
        info_ny = ticker_ny.info
        info_usd = ticker_usd.info
        
        # Pega a porcentagem exata que o Yahoo já calculou
        v_ny = info_ny.get('regularMarketChangePercent', 0.0) / 100
        v_usd = info_usd.get('regularMarketChangePercent', 0.0) / 100
        
        cot_ny = info_ny.get('regularMarketPrice', 0.0)
        cot_usd = info_usd.get('regularMarketPrice', 0.0)
        
        return cot_ny, v_ny, cot_usd, v_usd
    except:
        return 0.0, 0.0, 0.0, 0.0

def add_bg_and_style(image_file):
    if os.path.exists(image_file):
        with open(image_file, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), url("data:image/avif;base64,{encoded_string}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}
            h1, h2, h3, p, span, label, div {{
                color: white !important;
                text-shadow: 2px 2px 4px rgba(0,0,0,1) !important;
            }}
            .main-title {{
                text-align: center;
                font-size: 50px !important;
                font-weight: bold;
                margin-bottom: 20px;
                color: #F1C40F !important;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

# --- 2. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Previsão Café ES", page_icon="☕", layout="wide")

# ATENÇÃO: Renomeie o arquivo baixado para 'fundo_cafe.avif'
add_bg_and_style('fundo_cafe.avif')

st.markdown('<h1 class="main-title">Previsao do Cafe ☕</h1>', unsafe_allow_html=True)

# Chamada das funções agora que elas já existem no código
base_dura, base_rio = buscar_dados_cccv()
ny_p, ny_v, usd_p, usd_v = buscar_mercado()

# --- 3. CONTEÚDO DO SITE ---
st.divider()
st.markdown("### 📖 Como funciona este Painel?")
st.write("Este site realiza uma simulação do impacto do mercado financeiro global no preço físico do café no Espírito Santo.")

exp_col1, exp_col2, exp_col3 = st.columns(3)
with exp_col1:
    st.markdown("**1. Preço Base (CCCV)**")
    st.write("Buscamos diariamente as cotações oficiais de Bebida Dura e Bebida Rio.")
with exp_col2:
    st.markdown("**2. Variação Combinada**")
    st.write("Monitoramos a oscilação da Bolsa de Nova York e do Dólar.")
with exp_col3:
    st.markdown("**3. Alvo Estimado**")
    st.write("Aplicamos as variações sobre o preço base.")

st.info("⚠️ **Aviso:** Este site está em fase de testes.")
st.markdown("<h1 style='text-align: center;'>Criado por: Marcos Gomes</h1>", unsafe_allow_html=True)

if ny_p == 0:
    st.warning("Carregando dados da bolsa...")
else:
    var_total = ny_v + usd_v
    cor_tendencia = "#00FF00" if var_total >= 0 else "#FF0000"

    c1, c2, c3 = st.columns(3)
    c1.metric("Bolsa NY (Arábica)", f"{ny_p:.2f} pts", f"{ny_v:.2%}")
    c2.metric("Dólar Comercial", f"R$ {usd_p:.2f}", f"{usd_v:.2%}")
    c3.metric("Tendência Combinada", f"{(var_total*100):.2f}%")

    st.divider()
    col_d, col_r = st.columns(2)

    mudanca_dura = base_dura * var_total
    with col_d:
        st.subheader("☕ Bebida DURA")
        st.markdown(f"<h2 style='color:{cor_tendencia} !important; font-size: 40px;'>R$ {base_dura + mudanca_dura:.2f}</h2>", unsafe_allow_html=True)
        st.metric(label="Alvo Estimado", value="", delta=float(round(mudanca_dura, 2)))

    mudanca_rio = base_rio * var_total
    with col_r:
        st.subheader("☕ Bebida RIO")
        st.markdown(f"<h2 style='color:{cor_tendencia} !important; font-size: 40px;'>R$ {base_rio + mudanca_rio:.2f}</h2>", unsafe_allow_html=True)
        st.metric(label="Alvo Estimado", value="", delta=float(round(mudanca_rio, 2)))

st.divider()
st.caption("Atualizado via CCCV e Yahoo Finance.")
