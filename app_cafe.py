import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import base64
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Previsão Café ES", page_icon="☕", layout="wide")

# --- 2. FUNÇÕES DE BUSCA ---
def buscar_dados_precos():
    url = "https://www.cccv.org.br/cotacao/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        tabelas = pd.read_html(response.text)
        df = tabelas[0]
        
        # Preços Base
        dura = float(str(df.loc[df[0].str.contains("dura", case=False), 1].values[0]).replace('.', '').replace(',', '.'))
        rio = float(str(df.loc[df[0].str.contains("rio", case=False), 1].values[0]).replace('.', '').replace(',', '.'))
        # Base Conilon (Aqui você pode ajustar o valor fixo de MG se preferir)
        conilon = float(str(df.loc[df[0].str.contains("conilon", case=False), 1].values[0]).replace('.', '').replace(',', '.'))
        
        return dura, rio, conilon
    except:
        return 1690.00, 1330.00, 1440.00 

def buscar_mercado():
    try:
        # NY (Arábica) | Londres (Conilon) | Dólar
        # Usamos history(period="2d") para garantir o cálculo da porcentagem
        tk_ny = yf.Ticker("KC=F").history(period="2d")
        tk_lon = yf.Ticker("RC=F").history(period="2d")
        tk_usd = yf.Ticker("USDBRL=X").history(period="2d")
        
        # Cálculo Arábica NY
        cot_ny = tk_ny['Close'].iloc[-1]
        v_ny = (cot_ny / tk_ny['Close'].iloc[-2]) - 1
        
        # Cálculo Conilon Londres
        cot_lon = tk_lon['Close'].iloc[-1]
        v_lon = (cot_lon / tk_lon['Close'].iloc[-2]) - 1
        
        # Cálculo Dólar
        cot_usd = tk_usd['Close'].iloc[-1]
        v_usd = (cot_usd / tk_usd['Close'].iloc[-2]) - 1
        
        return cot_ny, v_ny, cot_lon, v_lon, cot_usd, v_usd
    except:
        return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

# --- 3. ESTILO ---
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
            .main-title {{ text-align: center; font-size: 50px !important; font-weight: bold; margin-bottom: 20px; }}
            </style>
            """,
            unsafe_allow_html=True
        )

# --- 4. EXECUÇÃO ---
add_bg_and_style('fundo_cafe_fazenda.avif')
st.markdown('<h1 class="main-title">Previsão do Café ☕</h1>', unsafe_allow_html=True)

base_dura, base_rio, base_conilon = buscar_dados_precos()
ny_p, ny_v, lon_p, lon_v, usd_p, usd_v = buscar_mercado()

if ny_p == 0:
    st.warning("Aguardando dados das bolsas...")
else:
    # --- TENDÊNCIAS SEPARADAS ---
    tendencia_arabica = ny_v + usd_v
    tendencia_conilon = lon_v + usd_v
    
    cor_ara = "#00FF00" if tendencia_arabica >= 0 else "#FF4B4B"
    cor_con = "#00FF00" if tendencia_conilon >= 0 else "#FF4B4B"

    # Métricas de Mercado (Agora com porcentagens calculadas)
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("NY (Arábica)", f"{ny_p:.2f} pts", f"{ny_v:.2%}")
    m2.metric("Londres (Conilon)", f"{lon_p:.0f} USD", f"{v_lon:.2%}")
    m3.metric("Dólar", f"R$ {usd_p:.2f}", f"{usd_v:.2%}")
    m4.metric("Tendência Arábica", f"{tendencia_arabica:.2%}")
    m5.metric("Tendência Conilon", f"{tendencia_conilon:.2%}")

    st.divider()
    
    col_d, col_r, col_c = st.columns(3)

    with col_d:
        st.subheader("☕ Bebida DURA")
        v_final_d = base_dura * (1 + tendencia_arabica)
        st.markdown(f"<h2 style='color:{cor_ara} !important;'>R$ {v_final_d:.2f}</h2>", unsafe_allow_html=True)
        st.caption(f"Base ES: R$ {base_dura:.2f}")

    with col_r:
        st.subheader("☕ Bebida RIO")
        v_final_r = base_rio * (1 + tendencia_arabica)
        st.markdown(f"<h2 style='color:{cor_ara} !important;'>R$ {v_final_r:.2f}</h2>", unsafe_allow_html=True)
        st.caption(f"Base ES: R$ {base_rio:.2f}")

    with col_c:
        st.subheader("☕ CONILON (MG)")
        v_final_c = base_conilon * (1 + tendencia_conilon)
        st.markdown(f"<h2 style='color:{cor_con} !important;'>R$ {v_final_c:.2f}</h2>", unsafe_allow_html=True)
        st.caption(f"Base Minas: R$ {base_conilon:.2f}")

st.divider()
with st.expander("🧐 Entenda as Tendências"):
    st.write(f"**Tendência Arábica:** Variação NY ({ny_v:.2%}) + Variação Dólar ({usd_v:.2%})")
    st.write(f"**Tendência Conilon:** Variação Londres ({v_lon:.2%}) + Variação Dólar ({usd_v:.2%})")
