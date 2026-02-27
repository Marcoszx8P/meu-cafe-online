import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import base64
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Previsão Café ES", page_icon="☕", layout="wide")

# --- 2. FUNÇÕES DE BUSCA ---
def buscar_dados_cccv():
    url = "https://www.cccv.org.br/cotacao/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        tabelas = pd.read_html(response.text)
        df = tabelas[0]
        dura_str = df.loc[df[0].str.contains("dura", case=False), 1].values[0]
        rio_str = df.loc[df[0].str.contains("rio", case=False), 1].values[0]
        conilon_str = df.loc[df[0].str.contains("conilon", case=False), 1].values[0]
        
        dura = float(str(dura_str).replace('.', '').replace(',', '.'))
        rio = float(str(rio_str).replace('.', '').replace(',', '.'))
        conilon = float(str(conilon_str).replace('.', '').replace(',', '.'))
        return dura, rio, conilon
    except:
        return 1694.00, 1349.00, 1250.00 

def buscar_mercado():
    try:
        # Usando download em lote para evitar bloqueios e garantir que os dados venham
        tickers = ["KC=F", "LRC=F", "USDBRL=X"]
        dados = yf.download(tickers, period="2d", interval="1d", progress=False)
        
        if dados.empty:
            return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

        # Preços atuais
        ny_p = dados['Close']['KC=F'].iloc[-1]
        lon_p = dados['Close']['LRC=F'].iloc[-1]
        usd_p = dados['Close']['USDBRL=X'].iloc[-1]

        # Variações
        v_ny = (ny_p / dados['Close']['KC=F'].iloc[-2]) - 1
        v_lon = (lon_p / dados['Close']['LRC=F'].iloc[-2]) - 1
        v_usd = (usd_p / dados['Close']['USDBRL=X'].iloc[-2]) - 1
        
        return ny_p, v_ny, lon_p, v_lon, usd_p, v_usd
    except:
        return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

# --- 3. FUNÇÃO DE ESTILO E FUNDO ---
def add_bg_and_style(image_file):
    if os.path.exists(image_file):
        with open(image_file, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url("data:image/avif;base64,{encoded_string}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}
            h1, h2, h3, p, span, label, div {{
                color: #FFFFFF !important;
                text-shadow: 2px 2px 8px rgba(0,0,0,1) !important;
            }}
            .main-title {{
                text-align: center;
                font-size: 50px !important;
                font-weight: bold;
                margin-bottom: 20px;
                color: #FFFFFF !important;
            }}
            [data-testid="stMetricValue"] {{
                color: white !important;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    else:
        st.sidebar.error(f"Erro: O arquivo '{image_file}' não foi encontrado.")

# --- 4. EXECUÇÃO DO PAINEL ---
add_bg_and_style('fundo_cafe_fazenda.avif')

st.markdown('<h1 class="main-title">Previsao do Cafe ☕</h1>', unsafe_allow_html=True)

base_dura, base_rio, base_conilon = buscar_dados_cccv()
ny_p, ny_v, lon_p, lon_v, usd_p, usd_v = buscar_mercado()

st.divider()

# CORREÇÃO DO ERRO DE CARREGAMENTO:
if ny_p == 0 or lon_p == 0:
    st.warning("Carregando dados das bolsas mundiais... Se demorar, tente atualizar a página.")
    # Força uma pequena pausa e tenta novamente se rodar localmente
    st.button("Atualizar Dados Manulamente")
else:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Bolsa NY (Arábica)", f"{ny_p:.2f} pts", f"{ny_v:.2%}")
    c2.metric("Bolsa Londres (Conilon)", f"{lon_p:.2f} pts", f"{lon_v:.2%}")
    c3.metric("Dólar Comercial", f"R$ {usd_p:.2f}", f"{usd_v:.2%}")
    
    var_total_arabica = ny_v + usd_v
    var_total_conilon = lon_v + usd_v
    
    c4.metric("Tendência Arábica", f"{(var_total_arabica*100):.2f}%")

    st.divider()
    
    st.markdown("### 🌿 Café Arábica")
    col_d, col_r = st.columns(2)
    cor_tendencia_a = "#00FF00" if var_total_arabica >= 0 else "#FF4B4B"

    mudanca_dura = base_dura * var_total_arabica
    with col_d:
        st.subheader("☕ Bebida DURA")
        st.markdown(f"<h2 style='color:{cor_tendencia_a} !important; font-size: 40px;'>R$ {base_dura + mudanca_dura:.2f}</h2>", unsafe_allow_html=True)
        st.metric(label="Alvo Estimado", value="", delta=float(round(mudanca_dura, 2)), delta_color="normal")

    mudanca_rio = base_rio * var_total_arabica
    with col_r:
        st.subheader("☕ Bebida RIO")
        st.markdown(f"<h2 style='color:{cor_tendencia_a} !important; font-size: 40px;'>R$ {base_rio + mudanca_rio:.2f}</h2>", unsafe_allow_html=True)
        st.metric(label="Alvo Estimado", value="", delta=float(round(mudanca_rio, 2)), delta_color="normal")

    st.divider()

    st.markdown("### 🍂 Café Conilon")
    col_c, col_info_c = st.columns(2)
    cor_tendencia_c = "#00FF00" if var_total_conilon >= 0 else "#FF4B4B"

    mudanca_conilon = base_conilon * var_total_conilon
    with col_c:
        st.subheader("☕ Conilon (7/8)")
        st.markdown(f"<h2 style='color:{cor_tendencia_c} !important; font-size: 40px;'>R$ {base_conilon + mudanca_conilon:.2f}</h2>", unsafe_allow_html=True)
        st.metric(label="Alvo Estimado", value="", delta=float(round(mudanca_conilon, 2)), delta_color="normal")
    
    with col_info_c:
        st.write(f"Variação Combinada (Londres + Dólar): **{var_total_conilon:.2%}**")

st.divider()
st.caption("Atualizado via CCCV e Yahoo Finance.")
