import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import base64
import os
from datetime import datetime

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Painel do Café ☕", page_icon="☕", layout="wide")

# --- 2. ESTILO E FUNDO ---
def add_bg_and_style(image_file):
    if os.path.exists(image_file):
        with open(image_file, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), url("data:image/avif;base64,{{encoded_string}}");
                background-size: cover; background-position: center; background-attachment: fixed;
            }}
            h1, h2, h3, p, span, label, div {{
                color: #FFFFFF !important; text-shadow: 2px 2px 8px rgba(0,0,0,1) !important;
            }}
            .main-title {{ text-align: center; font-size: 50px !important; font-weight: bold; margin-bottom: 10px; color: #F1C40F !important; }}
            </style>
            """,
            unsafe_allow_html=True
        )

# --- 3. FUNÇÃO ROBUSTA DE BUSCA ---
def buscar_dados_completos():
    # Inicia com valores padrão (Segurança contra erros)
    resultados = {
        'ny_p': 280.0, 'ny_v': 0.0, 'lon_p': 4500.0, 'lon_v': 0.0, 
        'usd_p': 5.13, 'usd_v': 0.0, 'b_dura': 1690.0, 'b_rio': 1330.0, 'b_con': 1440.0
    }

    # Busca Preços Físicos (CCCV)
    try:
        res = requests.get("https://www.cccv.org.br/cotacao/", headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        df_f = pd.read_html(res.text)[0]
        resultados['b_dura'] = float(str(df_f.loc[df_f[0].str.contains("dura", case=False), 1].values[0]).replace('.', '').replace(',', '.'))
        resultados['b_rio'] = float(str(df_f.loc[df_f[0].str.contains("rio", case=False), 1].values[0]).replace('.', '').replace(',', '.'))
        resultados['b_con'] = float(str(df_f.loc[df_f[0].str.contains("conilon", case=False), 1].values[0]).replace('.', '').replace(',', '.'))
    except: pass

    # Busca Mercado (Yahoo Finance) com tratamento de erro por ativo
    for ticker, chave_p, chave_v in [("KC=F", 'ny_p', 'ny_v'), ("RC=F", 'lon_p', 'lon_v'), ("USDBRL=X", 'usd_p', 'usd_v')]:
        try:
            data = yf.download(ticker, period="5d", interval="1d", progress=False)['Close'].dropna()
            if not data.empty and len(data) >= 2:
                resultados[chave_p] = float(data.iloc[-1])
                resultados[chave_v] = (float(data.iloc[-1]) / float(data.iloc[-2])) - 1
        except: continue
            
    return resultados

# --- 4. EXECUÇÃO ---
add_bg_and_style('fundo_cafe_fazenda.avif')
st.markdown('<h1 class="main-title">Painel do Café ☕</h1>', unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center;'>Atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>", unsafe_allow_html=True)

# Coleta os dados (sempre retornará algo, evitando o NameError)
d = buscar_dados_completos()

# Cálculos de Tendência
t_arabica = d['ny_v'] + d['usd_v']
t_conilon = d['lon_v'] + d['usd_v']
cor_ara = "#00FF00" if t_arabica >= 0 else "#FF4B4B"
cor_con = "#00FF00" if t_conilon >= 0 else "#FF4B4B"

# Layout de Métricas
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("NY (Arábica)", f"{d['ny_p']:.2f} pts", f"{d['ny_v']:.2%}")
m2.metric("Londres (Conilon)", f"{d['lon_p']:.0f} USD", f"{d['lon_v']:.2%}")
m3.metric("Dólar", f"R$ {d['usd_p']:.2f}", f"{d['usd_v']:.2%}")
m4.metric("Tendência Arábica", f"{t_arabica:.2%}")
m5.metric("Tendência Conilon", f"{t_conilon:.2%}")

st.divider()

# Colunas de Preço Alvo
c1, c2, c3 = st.columns(3)
with c1:
    st.subheader("☕ Bebida DURA")
    st.markdown(f"<h2 style='color:{cor_ara}; font-size: 42px;'>R$ {d['b_dura'] * (1+t_arabica):.2f}</h2>", unsafe_allow_html=True)
    st.caption(f"Base ES: R$ {d['b_dura']:.2f}")

with c2:
    st.subheader("☕ Bebida RIO")
    st.markdown(f"<h2 style='color:{cor_ara}; font-size: 42px;'>R$ {d['b_rio'] * (1+t_arabica):.2f}</h2>", unsafe_allow_html=True)
    st.caption(f"Base ES: R$ {d['b_rio']:.2f}")

with c3:
    st.subheader("☕ CONILON (MG)")
    st.markdown(f"<h2 style='color:{cor_con}; font-size: 42px;'>R$ {d['b_con'] * (1+t_conilon):.2f}</h2>", unsafe_allow_html=True)
    st.caption(f"Base Minas: R$ {d['b_con']:.2f}")

st.divider()

with st.expander("🧐 Como funciona o cálculo?"):
    st.write(f"**Arábica:** Bolsa NY ({d['ny_v']:.2%}) + Dólar ({d['usd_v']:.2%}) = {t_arabica:.2%}")
    st.write(f"**Conilon:** Bolsa Londres ({d['lon_v']:.2%}) + Dólar ({d['usd_v']:.2%}) = {t_conilon:.2%}")

st.markdown("<p style='text-align: center; opacity: 0.7;'>Criado por: Marcos Gomes</p>", unsafe_allow_html=True)
