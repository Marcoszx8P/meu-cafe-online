import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import base64
import os

# Configuração da página
st.set_page_config(page_title="Previsão Café ES", page_icon="☕", layout="wide")

# --- FUNÇÃO PARA IMAGEM DE FUNDO ---
def add_bg_from_local(image_file):
    if os.path.exists(image_file):
        with open(image_file, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("data:image/jpg;base64,{encoded_string}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}
            h1, h2, h3, p, span, label, .stMetric {{
                color: white !important;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

# Tenta carregar a imagem (Garanta que o nome do arquivo no GitHub seja IGUAL a este)
add_bg_from_local('historia_do_cafe-968x660-1-968x560.jpg')

def buscar_dados_cccv():
    url = "https://www.cccv.org.br/cotacao/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        tabelas = pd.read_html(response.text)
        df = tabelas[0]
        # Pegando os valores do CCCV
        dura_str = df.loc[df[0].str.contains("dura", case=False), 1].values[0]
        rio_str = df.loc[df[0].str.contains("rio", case=False), 1].values[0]
        dura = float(str(dura_str).replace('.', '').replace(',', '.'))
        rio = float(str(rio_str).replace('.', '').replace(',', '.'))
        return dura, rio
    except:
        return 1694.00, 1349.00 

def buscar_mercado():
    try:
        cafe_ny = yf.download("KC=F", period="5d", interval="1d", progress=False)
        dolar = yf.download("USDBRL=X", period="5d", interval="1d", progress=False)
        cot_ny = float(cafe_ny['Close'].iloc[-1])
        v_ny = (cot_ny / float(cafe_ny['Close'].iloc[-2])) - 1
        cot_usd = float(dolar['Close'].iloc[-1])
        v_usd = (cot_usd / float(dolar['Close'].iloc[-2])) - 1
        return cot_ny, v_ny, cot_usd, v_usd
    except:
        return 0.0, 0.0, 0.0, 0.0

st.title("☕ Monitor de Tendência: Café Arábica ES")
st.markdown("---")

base_dura, base_rio = buscar_dados_cccv()
ny_p, ny_v, usd_p, usd_v = buscar_mercado()

if ny_p == 0:
    st.warning("Aguardando conexão com o mercado financeiro...")
else:
    var_total = ny_v + usd_v
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Bolsa NY (Arábica)", f"{ny_p:.2f} pts", f"{ny_v:.2%}")
    c2.metric("Dólar Comercial", f"R$ {usd_p:.2f}", f"{usd_v:.2%}")
    c3.metric("Tendência Combinada", f"{(var_total*100):.2f}%")

    st.markdown("---")
    col_d, col_r = st.columns(2)

    with col_d:
        st.subheader("Bebida DURA")
        valor_d = base_dura + (base_dura * var_total)
        st.metric("Alvo Estimado", f"R$ {valor_d:.2f}", f"{float(round(base_dura * var_total, 2))}")

    with col_r:
        st.subheader("Bebida RIO")
        valor_r = base_rio + (base_rio * var_total)
        st.metric("Alvo Estimado", f"R$ {valor_r:.2f}", f"{float(round(base_rio * var_total, 2))}")

st.markdown("<br><h2 style='text-align: center;'>Criado por: Marcos Gomes</h2>", unsafe_allow_html=True)
