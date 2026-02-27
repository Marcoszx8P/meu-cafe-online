import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import base64
import os

# Configuração da página
st.set_page_config(page_title="Previsão Café ES", page_icon="☕", layout="wide")

# --- FUNÇÃO DE FUNDO E ESTILO ---
def add_bg_and_style(image_file):
    if os.path.exists(image_file):
        with open(image_file, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), url("data:image/jpg;base64,{encoded_string}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}
            /* Estilização global */
            h1, h2, h3, p, span, label, div {{
                color: white !important;
                text-shadow: 2px 2px 4px rgba(0,0,0,1) !important;
            }}
            /* Título Principal */
            .main-title {{
                text-align: center;
                font-size: 50px !important;
                font-weight: bold;
                margin-bottom: 20px;
                color: #F1C40F !important; /* Cor dourada para o título principal */
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

add_bg_and_style('historia_do_cafe-968x660-1-968x560.jpg')

# --- TÍTULO PRINCIPAL NO TOPO ---
st.markdown('<h1 class="main-title">Previsao do Cafe ☕</h1>', unsafe_allow_html=True)

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
        # Aumentei para 7d para garantir que pegue o fechamento anterior mesmo em fins de semana
        cafe_ny = yf.download("KC=F", period="7d", interval="1d", progress=False)['Close']
        dolar = yf.download("USDBRL=X", period="7d", interval="1d", progress=False)['Close']
        
        # Limpeza para evitar erros de dados vazios (NaN)
        cafe_ny = cafe_ny.dropna()
        dolar = dolar.dropna()

        cot_ny = float(cafe_ny.iloc[-1])
        v_ny = (cot_ny / float(
