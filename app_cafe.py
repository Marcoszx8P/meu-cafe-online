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
        
        # Busca Bebida Dura, Rio e Conilon
        dura_str = df.loc[df[0].str.contains("dura", case=False), 1].values[0]
        rio_str = df.loc[df[0].str.contains("rio", case=False), 1].values[0]
        conilon_str = df.loc[df[0].str.contains("conilon", case=False), 1].values[0]
        
        dura = float(str(dura_str).replace('.', '').replace(',', '.'))
        rio = float(str(rio_str).replace('.', '').replace(',', '.'))
        conilon = float(str(conilon_str).replace('.', '').replace(',', '.'))
        
        return dura, rio, conilon
    except:
        return 1694.00, 1349.00, 1450.00 

def buscar_mercado():
    try:
        # NY = Arábica | Londres (RC=F) = Conilon/Robusta
        ticker_ny = yf.Ticker("KC=F")
        ticker_lon = yf.Ticker("RC=F")
        ticker_usd = yf.Ticker("USDBRL=X")
        
        info_ny = ticker_ny.info
        info_lon = ticker_lon.info
        info_usd = ticker_usd.info
        
        # Dados Arábica
        cot_ny = info_ny.get('regularMarketPrice', 0.0)
        v_ny = info_ny.get('regularMarketChangePercent', 0.0) / 100
        
        # Dados Conilon (Londres)
        cot_lon = info_lon.get('regularMarketPrice', 0.0)
        v_lon = info_lon.get('regularMarketChangePercent', 0.0) / 100
        
        # Dados Dólar
        cot_usd = info_usd.get('regularMarketPrice', 0.0)
        v_usd = info_usd.get('regularMarketChangePercent', 0.0) / 100
        
        return cot_ny, v_ny, cot_lon, v_lon, cot_usd, v_usd
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
            </style>
            """,
            unsafe_allow_html=True
        )

# --- 4. EXECUÇÃO DO PAINEL ---
add_bg_and_style('fundo_cafe_fazenda.avif')

st.markdown('<h1 class="main-title">Previsao do Cafe ☕</h1>', unsafe_allow_html=True)

# Chamando as funções
base_dura, base_rio, base_conilon = buscar_dados_cccv()
ny_p, ny_v, lon_p, lon_v, usd_p, usd_v = buscar_mercado()

st.divider()

if ny_p == 0:
    st.warning("Carregando dados da bolsa...")
else:
    # Variações Combinadas
    var_arabica = ny_v + usd_v
    var_conilon = lon_v + usd_v
    
    # Cores
    cor_ara = "#00FF00" if var_arabica >= 0 else "#FF4B4B"
    cor_con = "#00FF00" if var_conilon >= 0 else "#FF4B4B"

    # Métricas Principais
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Bolsa NY (Arábica)", f"{ny_p:.2f} pts", f"{ny_v:.2%}")
    c2.metric("Bolsa Londres (Conilon)", f"{lon_p:.2f} USD", f"{lon_v:.2%}")
    c3.metric("Dólar Comercial", f"R$ {usd_p:.2f}", f"{usd_v:.2%}")
    c4.metric("Tendência Conilon", f"{(var_conilon*100):.2f}%")

    st.divider()
    
    # Exibição dos Alvos
    col_d, col_r, col_c = st.columns(3)

    # BEBIDA DURA (Arábica)
    mudanca_dura = base_dura * var_arabica
    with col_d:
        st.subheader("☕ Bebida DURA")
        st.markdown(f"<h2 style='color:{cor_ara} !important; font-size: 35px;'>R$ {base_dura + mudanca_dura:.2f}</h2>", unsafe_allow_html=True)
        st.metric(label="Alvo Estimado", value="", delta=float(round(mudanca_dura, 2)))

    # BEBIDA RIO (Arábica)
    mudanca_rio = base_rio * var_arabica
    with col_r:
        st.subheader("☕ Bebida RIO")
        st.markdown(f"<h2 style='color:{cor_ara} !important; font-size: 35px;'>R$ {base_rio + mudanca_rio:.2f}</h2>", unsafe_allow_html=True)
        st.metric(label="Alvo Estimado", value="", delta=float(round(mudanca_rio, 2)))

    # CONILON (Londres)
    mudanca_conilon = base_conilon * var_conilon
    with col_c:
        st.subheader("☕ CONILON")
        st.markdown(f"<h2 style='color:{cor_con} !important; font-size: 35px;'>R$ {base_conilon + mudanca_conilon:.2f}</h2>", unsafe_allow_html=True)
        st.metric(label="Alvo Estimado", value="", delta=float(round(mudanca_conilon, 2)))

# --- EXPLICAÇÃO FINAL ---
st.divider()
with st.expander("🧐 Produtor, entenda a diferença entre Arábica e Conilon"):
    st.markdown("""
    * **Arábica (Dura e Rio):** O preço base segue a Bolsa de **Nova York**.
    * **Conilon:** O preço base segue a Bolsa de **Londres**, que é a referência mundial para o café Robusta/Conilon.
    * O cálculo do Alvo Estimado para ambos soma a variação da sua respectiva bolsa com a variação do dólar no dia.
    """)

st.caption("Atualizado via CCCV, Yahoo Finance (NY e Londres).")
