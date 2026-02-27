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
        # Busca Arábica (Dura e Rio) e Conilon (Tipo 7/8)
        response = requests.get(url, headers=headers, timeout=10)
        tabelas = pd.read_html(response.text)
        df = tabelas[0]
        
        dura_str = df.loc[df[0].str.contains("dura", case=False), 1].values[0]
        rio_str = df.loc[df[0].str.contains("rio", case=False), 1].values[0]
        # Tentativa de pegar o Conilon (ajuste o índice se necessário no site do CCCV)
        conilon_str = df.loc[df[0].str.contains("conilon", case=False), 1].values[0]

        dura = float(str(dura_str).replace('.', '').replace(',', '.'))
        rio = float(str(rio_str).replace('.', '').replace(',', '.'))
        conilon = float(str(conilon_str).replace('.', '').replace(',', '.'))
        
        return dura, rio, conilon
    except:
        # Valores padrão de fallback caso o site do CCCV esteja fora do ar
        return 1694.00, 1349.00, 1250.00 

def buscar_mercado():
    try:
        ticker_ny = yf.Ticker("KC=F")      # Arábica NY
        ticker_lon = yf.Ticker("RC=F")     # Robusta/Conilon Londres
        ticker_usd = yf.Ticker("USDBRL=X") # Dólar
        
        # Dados NY
        cot_ny = ticker_ny.info.get('regularMarketPrice', 0.0)
        v_ny = ticker_ny.info.get('regularMarketChangePercent', 0.0) / 100
        
        # Dados Londres
        cot_lon = ticker_lon.info.get('regularMarketPrice', 0.0)
        v_lon = ticker_lon.info.get('regularMarketChangePercent', 0.0) / 100
        
        # Dados Dólar
        cot_usd = ticker_usd.info.get('regularMarketPrice', 0.0)
        v_usd = ticker_usd.info.get('regularMarketChangePercent', 0.0) / 100
        
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
            [data-testid="stMetricValue"] {{
                color: white !important;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    else:
        st.sidebar.error(f"Erro: O arquivo '{image_file}' não foi encontrado.")

# --- 4. EXECUÇÃO ---
add_bg_and_style('fundo_cafe_fazenda.avif')

st.markdown('<h1 class="main-title">Previsão do Café Capixaba ☕</h1>', unsafe_allow_html=True)

# Chamada das funções
base_dura, base_rio, base_conilon = buscar_dados_cccv()
ny_p, ny_v, lon_p, lon_v, usd_p, usd_v = buscar_mercado()

st.divider()

if ny_p == 0 or lon_p == 0:
    st.warning("Carregando dados das bolsas mundiais...")
else:
    # 1. MERCADO FINANCEIRO (MÉTRICAS)
    st.markdown("### 📊 Mercado Financeiro em Tempo Real")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("NY (Arábica)", f"{ny_p:.2f} pts", f"{ny_v:.2%}")
    m2.metric("Londres (Conilon)", f"${lon_p:.0f}/t", f"{lon_v:.2%}")
    m3.metric("Dólar Comercial", f"R$ {usd_p:.2f}", f"{usd_v:.2%}")
    
    # 2. ÁREA DO CAFÉ ARÁBICA
    st.divider()
    st.markdown("## 🌿 Tendência: Café Arábica (Base NY + Dólar)")
    var_arabica = ny_v + usd_v
    cor_arabica = "#00FF00" if var_arabica >= 0 else "#FF4B4B"
    
    col_d, col_r = st.columns(2)
    # Bebida Dura
    mudanca_dura = base_dura * var_arabica
    with col_d:
        st.subheader("☕ Arábica: Bebida DURA")
        st.markdown(f"<h2 style='color:{cor_arabica} !important; font-size: 40px;'>R$ {base_dura + mudanca_dura:.2f}</h2>", unsafe_allow_html=True)
        st.metric(label="Alvo Estimado (Variação)", value="", delta=f"R$ {mudanca_dura:.2f}")

    # Bebida Rio
    mudanca_rio = base_rio * var_arabica
    with col_r:
        st.subheader("☕ Arábica: Bebida RIO")
        st.markdown(f"<h2 style='color:{cor_arabica} !important; font-size: 40px;'>R$ {base_rio + mudanca_rio:.2f}</h2>", unsafe_allow_html=True)
        st.metric(label="Alvo Estimado (Variação)", value="", delta=f"R$ {mudanca_rio:.2f}")

    # 3. ÁREA DO CAFÉ CONILON
    st.divider()
    st.markdown("## 🍂 Tendência: Café Conilon (Base Londres + Dólar)")
    var_conilon = lon_v + usd_v
    cor_conilon = "#00FF00" if var_conilon >= 0 else "#FF4B4B"
    
    col_c1, col_c2 = st.columns([1, 1])
    mudanca_conilon = base_conilon * var_conilon
    with col_c1:
        st.subheader("☕ Conilon (Tipo 7/8)")
        st.markdown(f"<h2 style='color:{cor_conilon} !important; font-size: 40px;'>R$ {base_conilon + mudanca_conilon:.2f}</h2>", unsafe_allow_html=True)
        st.metric(label="Alvo Estimado (Variação)", value="", delta=f"R$ {mudanca_conilon:.2f}")
    with col_c2:
        st.write("")
        st.write(f"**Preço Base CCCV:** R$ {base_conilon:.2f}")
        st.write(f"**Tendência Combinada:** {(var_conilon*100):.2f}%")

st.divider()
st.markdown("<h3 style='text-align: center;'>Criado por: Marcos Gomes</h3>", unsafe_allow_html=True)

with st.expander("🧐 Entenda o cálculo do Conilon"):
    st.markdown("""
    O café **Conilon** (Robusta) é negociado na **Bolsa de Londres (ICE Europe)**. 
    * O cálculo aqui soma a variação de Londres com a variação do Dólar.
    * Se Londres sobe 2% e o Dólar cai 1%, a tendência do Conilon no ES é de uma alta aproximada de 1%.
    """)

st.caption("Fontes: CCCV Vitória, Yahoo Finance (Bolsas de NY e Londres).")
