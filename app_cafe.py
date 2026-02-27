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
    # Valores padrão (caso o site falhe)
    dura, rio, conilon = 1700.0, 1350.0, 1200.0
    try:
        response = requests.get(url, headers=headers, timeout=10)
        tabelas = pd.read_html(response.text)
        df = tabelas[0]
        
        # Busca flexível por contém texto
        dura = float(df[df[0].str.contains("Dura", case=False, na=False)][1].values[0].replace('.', '').replace(',', '.'))
        rio = float(df[df[0].str.contains("Rio", case=False, na=False)][1].values[0].replace('.', '').replace(',', '.'))
        conilon = float(df[df[0].str.contains("Conilon", case=False, na=False)][1].values[0].replace('.', '').replace(',', '.'))
    except Exception as e:
        st.sidebar.warning(f"Usando preços base (CCCV indisponível)")
    return dura, rio, conilon

def buscar_mercado():
    try:
        # Tickers: KC=F (Arábica NY), LRC=F (Robusta Londres), USDBRL=X (Dólar)
        tickers = yf.download(["KC=F", "LRC=F", "USDBRL=X"], period="2d", interval="1d", group_by='ticker', progress=False)
        
        def get_data(ticker):
            curr = tickers[ticker]['Close'].iloc[-1]
            prev = tickers[ticker]['Close'].iloc[-2]
            var = (curr - prev) / prev
            return curr, var

        ny_p, ny_v = get_data("KC=F")
        lon_p, lon_v = get_data("LRC=F")
        usd_p, usd_v = get_data("USDBRL=X")
        
        return ny_p, ny_v, lon_p, lon_v, usd_p, usd_v
    except:
        return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

# --- 3. ESTILO ---
def add_bg_and_style(image_file):
    if os.path.exists(image_file):
        with open(image_file, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode()
        st.markdown(f"""
            <style>
            .stApp {{
                background-image: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), url("data:image/avif;base64,{encoded_string}");
                background-size: cover; background-attachment: fixed;
            }}
            h1, h2, h3, span, label {{ color: white !important; text-shadow: 2px 2px 4px #000; }}
            [data-testid="stMetricValue"] {{ color: white !important; font-weight: bold; }}
            </style>
            """, unsafe_allow_html=True)

# --- 4. DASHBOARD ---
add_bg_and_style('fundo_cafe_fazenda.avif')

st.markdown("<h1 style='text-align: center;'>Previsão do Café Capixaba ☕</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Criado por: Marcos Gomes</p>", unsafe_allow_html=True)

base_dura, base_rio, base_conilon = buscar_dados_cccv()
ny_p, ny_v, lon_p, lon_v, usd_p, usd_v = buscar_mercado()

if ny_p == 0:
    st.error("Erro ao conectar com Yahoo Finance. Tente atualizar a página.")
else:
    # Métricas Principais
    m1, m2, m3 = st.columns(3)
    m1.metric("NY (Arábica)", f"{ny_p:.2f} pts", f"{ny_v:.2%}")
    m2.metric("Londres (Conilon)", f"${lon_p:.0f}/t", f"{lon_v:.2%}")
    m3.metric("Dólar", f"R$ {usd_p:.2f}", f"{usd_v:.2%}")

    st.divider()

    # --- ARÁBICA ---
    st.subheader("🌿 Café Arábica (Impacto NY + Dólar)")
    col1, col2 = st.columns(2)
    var_arabica = ny_v + usd_v
    cor_a = "#00FF00" if var_arabica >= 0 else "#FF4B4B"
    
    with col1:
        valor = base_dura * (1 + var_arabica)
        st.markdown(f"**Bebida DURA**")
        st.markdown(f"<h2 style='color:{cor_a} !important;'>R$ {valor:.2f}</h2>", unsafe_allow_html=True)
        st.caption(f"Base CCCV: R$ {base_dura:.2f}")

    with col2:
        valor = base_rio * (1 + var_arabica)
        st.markdown(f"**Bebida RIO**")
        st.markdown(f"<h2 style='color:{cor_a} !important;'>R$ {valor:.2f}</h2>", unsafe_allow_html=True)
        st.caption(f"Base CCCV: R$ {base_rio:.2f}")

    st.divider()

    # --- CONILON ---
    st.subheader("🍂 Café Conilon (Impacto Londres + Dólar)")
    var_conilon = lon_v + usd_v
    cor_c = "#00FF00" if var_conilon >= 0 else "#FF4B4B"
    
    c_col1, c_col2 = st.columns(2)
    with c_col1:
        valor_c = base_conilon * (1 + var_conilon)
        st.markdown(f"**Conilon Tipo 7/8**")
        st.markdown(f"<h2 style='color:{cor_c} !important;'>R$ {valor_c:.2f}</h2>", unsafe_allow_html=True)
        st.caption(f"Base CCCV: R$ {base_conilon:.2f}")
    with c_col2:
        st.metric("Tendência Conilon", f"{(var_conilon*100):.2f}%", delta_color="normal")

st.divider()
with st.expander("📊 Metodologia"):
    st.write("O cálculo soma a variação percentual da bolsa correspondente (NY para Arábica, Londres para Conilon) à variação do dólar, aplicando o resultado sobre o preço físico do CCCV.")

st.caption("Dados: CCCV Vitória | Yahoo Finance")
