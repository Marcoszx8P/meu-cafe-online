import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import base64
import os

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Previsão Café ES", page_icon="☕", layout="wide")

# 2. FUNÇÕES DE BUSCA (Definir antes de usar)
def buscar_dados_cccv():
    url = "https://www.cccv.org.br/cotacao/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        tabelas = pd.read_html(response.text)
        df = tabelas[0]
        # Pegando os valores
        dura_str = df.loc[df[0].str.contains("dura", case=False), 1].values[0]
        rio_str = df.loc[df[0].str.contains("rio", case=False), 1].values[0]
        dura = float(str(dura_str).replace('.', '').replace(',', '.'))
        rio = float(str(rio_str).replace('.', '').replace(',', '.'))
        return dura, rio
    except Exception as e:
        # Valores de fallback caso o site do CCCV esteja fora do ar
        return 1694.00, 1349.00 

def buscar_mercado():
    try:
        # Pegando dados diretos via Ticker para evitar cálculos manuais
        tk_ny = yf.Ticker("KC=F")
        tk_usd = yf.Ticker("USDBRL=X")
        
        # .info traz a numeração que o Yahoo já calculou
        info_ny = tk_ny.info
        info_usd = tk_usd.info
        
        # Preço Atual
        cot_ny = info_ny.get('regularMarketPrice', 0.0)
        cot_usd = info_usd.get('regularMarketPrice', 0.0)
        
        # PEGANDO A PORCENTAGEM DIRETA DO YAHOO (ex: -0.80)
        # Dividimos por 100 para o Streamlit entender como decimal de porcentagem
        v_ny = info_ny.get('regularMarketChangePercent', 0.0) / 100
        v_usd = info_usd.get('regularMarketChangePercent', 0.0) / 100
        
        return cot_ny, v_ny, cot_usd, v_usd
    except:
        return 0.0, 0.0, 0.0, 0.0

# 3. ESTILIZAÇÃO
def add_bg_and_style(image_file):
    if os.path.exists(image_file):
        with open(image_file, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode()
        st.markdown(f"""
            <style>
            .stApp {{
                background-image: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), url("data:image/jpg;base64,{encoded_string}");
                background-size: cover; background-position: center; background-attachment: fixed;
            }}
            h1, h2, h3, p, span, label, div {{ color: white !important; text-shadow: 2px 2px 4px rgba(0,0,0,1) !important; }}
            .main-title {{ text-align: center; font-size: 50px !important; font-weight: bold; margin-bottom: 20px; color: #F1C40F !important; }}
            </style>
            """, unsafe_allow_html=True)

add_bg_and_style('historia_do_cafe-968x660-1-968x560.jpg')

# 4. EXECUÇÃO DO PAINEL
st.markdown('<h1 class="main-title">Previsão do Café ☕</h1>', unsafe_allow_html=True)

# Chamada das funções
base_dura, base_rio = buscar_dados_cccv()
ny_p, ny_v, usd_p, usd_v = buscar_mercado()

st.divider()
st.markdown("### 📖 Como funciona este Painel?")
# ... (seu texto explicativo aqui) ...

if ny_p == 0:
    st.warning("Aguardando conexão com Yahoo Finance...")
else:
    var_total = ny_v + usd_v
    cor_tendencia = "#00FF00" if var_total >= 0 else "#FF0000"

    c1, c2, c3 = st.columns(3)
    c1.metric("Bolsa NY (Arábica)", f"{ny_p:.2f} pts", f"{ny_v:.2%}")
    c2.metric("Dólar Comercial", f"R$ {usd_p:.2f}", f"{usd_v:.2%}")
    c3.metric("Tendência Combinada", f"{(var_total*100):.2f}%")

    st.divider()
    col_d, col_r = st.columns(2)

    # BEBIDA DURA
    mudanca_dura = base_dura * var_total
    with col_d:
        st.subheader("☕ Bebida DURA")
        st.markdown(f"<h2 style='color:{cor_tendencia} !important; font-size: 40px;'>R$ {base_dura + mudanca_dura:.2f}</h2>", unsafe_allow_html=True)
        st.metric(label="Alvo Estimado", value="", delta=f"R$ {mudanca_dura:.2f}")

    # BEBIDA RIO
    mudanca_rio = base_rio * var_total
    with col_r:
        st.subheader("☕ Bebida RIO")
        st.markdown(f"<h2 style='color:{cor_tendencia} !important; font-size: 40px;'>R$ {base_rio + mudanca_rio:.2f}</h2>", unsafe_allow_html=True)
        st.metric(label="Alvo Estimado", value="", delta=f"R$ {mudanca_rio:.2f}")

st.markdown("<h3 style='text-align: center;'>Criado por: Marcos Gomes</h3>", unsafe_allow_html=True)
