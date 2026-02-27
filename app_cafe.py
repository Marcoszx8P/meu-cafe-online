import streamlit as st
import pandas as pd
import yfinance as yf
import requests

# Configuração da página para o site ficar bonito no celular e PC
st.set_page_config(page_title="Previsão Café ES", page_icon="☕", layout="wide")

# --- FUNÇÃO PARA BUSCAR PREÇOS NO CCCV (VITÓRIA) ---
def buscar_dados_cccv():
    url = "https://www.cccv.org.br/cotacao/"
    # Identificação para o site não bloquear o acesso automático
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        tabelas = pd.read_html(response.text)
        df = tabelas[0]
        
        # Localiza os preços nas linhas de Bebida Dura e Rio
        dura_str = df.loc[df[0].str.contains("dura", case=False), 1].values[0]
        rio_str = df.loc[df[0].str.contains("rio", case=False), 1].values[0]
        
        # Converte o formato brasileiro (1.600,00) para o formato matemático (1600.00)
        dura = float(dura_str.replace('.', '').replace(',', '.'))
        rio = float(rio_str.replace
