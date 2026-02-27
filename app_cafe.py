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
                background-image: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), url("data:image/avif;base64,{encoded_string}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}
            h1, h2, h3, p, span, label, div {{
                color: #FFFFFF !important;
                text-shadow: 2px 2px 8px rgba(0,0,0,1) !important;
            }}
            .main-title {{
                text-align: center; font-size: 50px !important; font-weight: bold; margin-bottom: 10px; color: #F1C40F !important;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

# --- 3. BUSCA DE DADOS ---
def buscar_dados():
    # Preços Físicos CCCV
    try:
        res = requests.get("https://www.cccv.org.br/cotacao/", headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        df_fisico = pd.read_html(res.text)[0]
        dura = float(str(df_fisico.loc[df_fisico[0].str.contains("dura", case=False), 1].values[0]).replace('.', '').replace(',', '.'))
        rio = float(str(df_fisico.loc[df_fisico[0].str.contains("rio", case=False), 1].values[0]).replace('.', '').replace(',', '.'))
        con_mg = float(str(df_fisico.loc[df_fisico[0].str.contains("conilon", case=False), 1].values[0]).replace('.', '').replace(',', '.'))
    except:
        dura, rio, con_mg = 1690.0, 1330.0, 1440.0

    # Mercado Financeiro
    try:
        ny = yf.download("KC=F", period="5d", interval="1d", progress=False)['Close'].dropna()
        lon = yf.download("RC=F", period="5d", interval="1d", progress=False)['Close'].dropna()
        usd = yf.download("USDBRL=X", period="5d", interval="1d", progress=False)['Close'].dropna()

        v_ny = (ny.iloc[-1] / ny.iloc[-2]) - 1
        v_lon = (lon.iloc[-1] / lon.iloc[-2]) - 1
        v_usd = (usd.iloc[-1] / usd.iloc[-2]) - 1

        return (float(ny.iloc[-1]), v_ny, float(lon.iloc[-1]), v_lon, float(usd.iloc[-1]), v_usd, dura, rio, con_mg)
    except:
        return None

# --- 4. EXECUÇÃO ---
add_bg_and_style('fundo_cafe_fazenda.avif')
st.markdown('<h1 class="main-title">Painel do Café ☕</h1>', unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center;'>Atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>", unsafe_allow_html=True)

dados = buscar_dados()

if dados is None:
    st.error("Erro ao carregar dados do Yahoo Finance. Verifique sua conexão ou tente atualizar a página.")
else:
    p_ny, v_ny, p_lon, v_lon, p_usd, v_usd, b_dura, b_rio, b_con = dados
    
    # Tendências
    t_arabica = v_ny + v_usd
    t_conilon = v_lon + v_usd
    
    # Cores
    c_ara = "#00FF00" if t_arabica >= 0 else "#FF4B4B"
    c_con = "#00FF00" if t_conilon >= 0 else "#FF4B4B"

    # Métricas
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("NY (Arábica)", f"{p_ny:.2f} pts", f"{v_ny:.2%}")
    m2.metric("Londres (Conilon)", f"{p_lon:.0f} USD", f"{v_lon:.2%}")
    m3.metric("Dólar", f"R$ {p_usd:.2f}", f"{v_usd:.2%}")
    m4.metric("Tendência Arábica", f"{t_arabica:.2%}")
    m5.metric("Tendência Conilon", f"{t_conilon:.2%}")

    st.divider()

    # Alvos
    c1, c2, c3 = st.columns(3)
    with c1:
        st.subheader("☕ Bebida DURA")
        st.markdown(f"<h2 style='color:{c_ara}; font-size: 42px;'>R$ {b_dura * (1+t_arabica):.2f}</h2>", unsafe_allow_html=True)
        st.caption(f"Base CCCV: R$ {b_dura:.2f}")
    with c2:
        st.subheader("☕ Bebida RIO")
        st.markdown(f"<h2 style='color:{c_ara}; font-size: 42px;'>R$ {b_rio * (1+t_arabica):.2f}</h2>", unsafe_allow_html=True)
        st.caption(f"Base CCCV: R$ {b_rio:.2f}")
    with c3:
        st.subheader("☕ CONILON (MG)")
        st.markdown(f"<h2 style='color:{c_con}; font-size: 42px;'>R$ {b_con * (1+t_conilon):.2f}</h2>", unsafe_allow_html=True)
        st.caption(f"Base Minas: R$ {b_con:.2f}")

    st.divider()
    
    # EXPLICAÇÃO (Agora dentro do IF, para evitar o NameError)
    with st.expander("🧐 Como funciona a somatória para chegar ao resultado?"):
        st.markdown(f"""
        1. **Arábica (Dura/Rio):** NY ({v_ny:.2%}) + Dólar ({v_usd:.2%}) = **{t_arabica:.2%}**.
        2. **Conilon:** Londres ({v_lon:.2%}) + Dólar ({v_usd:.2%}) = **{t_conilon:.2%}**.
        """)

st.markdown("<p style='text-align: center; opacity: 0.7;'>Criado por: Marcos Gomes</p>", unsafe_allow_html=True)
