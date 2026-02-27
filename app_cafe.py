import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import base64
import os

# Configuração da página
st.set_page_config(page_title="Previsão Café ES", page_icon="☕", layout="wide")

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

add_bg_and_style('historia_do_cafe-968x660-1-968x560.jpg')

st.markdown('<h1 class="main-title">Previsão do Café ☕</h1>', unsafe_allow_html=True)

def buscar_dados_cccv():
    url = "https://www.cccv.org.br/cotacao/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        tabelas = pd.read_html(response.text)
        df = tabelas[0]
        # Localiza as linhas que contém "Dura" e "Rio"
        dura_str = df[df[0].str.contains("Dura", case=False, na=False)][1].values[0]
        rio_str = df[df[0].str.contains("Rio", case=False, na=False)][1].values[0]
        
        dura = float(str(dura_str).replace('.', '').replace(',', '.'))
        rio = float(str(rio_str).replace('.', '').replace(',', '.'))
        return dura, rio
    except Exception as e:
        return 1694.00, 1349.00 

def buscar_mercado():
    try:
        # Buscamos um período maior para garantir que teremos os dois últimos pregões válidos
        cafe_ny = yf.download("KC=F", period="7d", interval="1d", progress=False)['Close']
        dolar = yf.download("USDBRL=X", period="7d", interval="1d", progress=False)['Close']
        
        # Ajuste para lidar com MultiIndex do yfinance se necessário
        if isinstance(cafe_ny, pd.DataFrame):
            cafe_ny = cafe_ny.iloc[:, 0]
        if isinstance(dolar, pd.DataFrame):
            dolar = dolar.iloc[:, 0]

        # Pegar os dois últimos valores não nulos
        cafe_ny = cafe_ny.dropna()
        dolar = dolar.dropna()

        cot_ny = float(cafe_ny.iloc[-1])
        prev_ny = float(cafe_ny.iloc[-2])
        v_ny = (cot_ny / prev_ny) - 1

        cot_usd = float(dolar.iloc[-1])
        prev_usd = float(dolar.iloc[-2])
        v_usd = (cot_usd / prev_usd) - 1

        return cot_ny, v_ny, cot_usd, v_usd
    except Exception as e:
        return 0.0, 0.0, 0.0, 0.0

# --- LÓGICA DE EXIBIÇÃO ---
base_dura, base_rio = buscar_dados_cccv()
ny_p, ny_v, usd_p, usd_v = buscar_mercado()

if ny_p == 0:
    st.warning("Aguardando resposta do Yahoo Finance... Tente atualizar a página.")
else:
    # A variação combinada correta é o produto das variações: (1+v1)*(1+v2) - 1
    var_total = ((1 + ny_v) * (1 + usd_v)) - 1
    cor_tendencia = "#00FF00" if var_total >= 0 else "#FF0000"

    c1, c2, c3 = st.columns(3)
    c1.metric("Bolsa NY (Arábica)", f"{ny_p:.2f} pts", f"{ny_v:.2%}")
    c2.metric("Dólar Comercial", f"R$ {usd_p:.4f}", f"{usd_v:.2%}")
    c3.metric("Tendência Real Combinada", f"{(var_total*100):.2f}%")

    st.divider()
    col_d, col_r = st.columns(2)

    # --- CÁLCULO DOS ALVOS ---
    preco_estimado_dura = base_dura * (1 + var_total)
    mudanca_reais_dura = preco_estimado_dura - base_dura

    preco_estimado_rio = base_rio * (1 + var_total)
    mudanca_reais_rio = preco_estimado_rio - base_rio

    with col_d:
        st.subheader("☕ Bebida DURA (Estimado)")
        st.markdown(f"<h2 style='color:{cor_tendencia} !important; font-size: 45px;'>R$ {preco_estimado_dura:.2f}</h2>", unsafe_allow_html=True)
        st.metric(label="Diferença vs Base CCCV", value=f"R$ {preco_estimado_dura:.2f}", delta=f"R$ {mudanca_reais_dura:.2f}")

    with col_r:
        st.subheader("☕ Bebida RIO (Estimado)")
        st.markdown(f"<h2 style='color:{cor_tendencia} !important; font-size: 45px;'>R$ {preco_estimado_rio:.2f}</h2>", unsafe_allow_html=True)
        st.metric(label="Diferença vs Base CCCV", value=f"R$ {preco_estimado_rio:.2f}", delta=f"R$ {mudanca_reais_rio:.2f}")

st.divider()
st.markdown("### 📖 Como funciona este Painel?")
st.write("O sistema projeta o preço físico do ES aplicando a variação percentual de NY e do Dólar sobre o último fechamento do CCCV.")
st.info("⚠️ **Aviso:** Valores aproximados baseados em fechamento de mercado.")
st.markdown("<h3 style='text-align: center;'>Criado por: Marcos Gomes</h3>", unsafe_allow_html=True)
