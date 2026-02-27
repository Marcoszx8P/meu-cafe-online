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
        
        # Busca Bebida Dura
        dura_str = df.loc[df[0].str.contains("dura", case=False), 1].values[0]
        dura = float(str(dura_str).replace('.', '').replace(',', '.'))
        
        # Busca Bebida Rio
        rio_str = df.loc[df[0].str.contains("rio", case=False), 1].values[0]
        rio = float(str(rio_str).replace('.', '').replace(',', '.'))
        
        # Busca Conilon (Tipo 7/8)
        conilon_str = df.loc[df[0].str.contains("7/8", case=False), 1].values[0]
        conilon = float(str(conilon_str).replace('.', '').replace(',', '.'))
        
        return dura, rio, conilon
    except:
        return 1694.00, 1349.00, 1100.00 

def buscar_mercado():
    try:
        ticker_ny = yf.Ticker("KC=F") # Arábica NY
        ticker_lon = yf.Ticker("RC=F") # Robusta Londres
        ticker_usd = yf.Ticker("USDBRL=X") # Dólar
        
        # Dados NY
        info_ny = ticker_ny.info
        cot_ny = info_ny.get('regularMarketPrice', 0.0)
        v_ny = info_ny.get('regularMarketChangePercent', 0.0) / 100
        
        # Dados Londres
        info_lon = ticker_lon.info
        cot_lon = info_lon.get('regularMarketPrice', 0.0)
        v_lon = info_lon.get('regularMarketChangePercent', 0.0) / 100
        
        # Dados Dólar
        info_usd = ticker_usd.info
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
            [data-testid="stMetricValue"] {{
                color: white !important;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    else:
        st.sidebar.error(f"Erro: O arquivo '{image_file}' não foi encontrado.")

# --- 4. EXECUÇÃO DO PAINEL ---
add_bg_and_style('fundo_cafe_fazenda.avif')

st.markdown('<h1 class="main-title">Previsao do Cafe ☕</h1>', unsafe_allow_html=True)

# Chamando as funções
base_dura, base_rio, base_conilon = buscar_dados_cccv()
ny_p, ny_v, lon_p, lon_v, usd_p, usd_v = buscar_mercado()

st.divider()
st.markdown("### 📖 Como funciona este Painel?")
st.write("Este site simula o impacto das bolsas mundiais e do dólar no preço do café no Espírito Santo.")

exp_col1, exp_col2, exp_col3 = st.columns(3)
with exp_col1:
    st.markdown("**1. Preço Base (CCCV)**")
    st.write("Cotações oficiais de Bebida Dura, Rio e Conilon diretamente do site do CCCV em Vitória.")
with exp_col2:
    st.markdown("**2. Diferencial de Bolsas**")
    st.write("O Arábica segue a Bolsa de **NY**, enquanto o Conilon segue a Bolsa de **Londres**.")
with exp_col3:
    st.markdown("**3. Alvo Estimado**")
    st.write("Somamos a variação da respectiva Bolsa + a variação do Dólar sobre o preço físico de hoje.")

st.info("⚠️ **Aviso:** Este site está em fase de testes. Os valores são estimativas matemáticas.")
st.markdown("<h1 style='text-align: center;'>Criado por: Marcos Gomes</h1>", unsafe_allow_html=True)

if ny_p == 0:
    st.warning("Carregando dados das bolsas...")
else:
    # Indicadores de Mercado
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Bolsa NY (Arábica)", f"{ny_p:.2f}", f"{ny_v:.2%}")
    m2.metric("Bolsa Londres (Robusta)", f"{lon_p:.2f}", f"{lon_v:.2%}")
    m3.metric("Dólar Comercial", f"R$ {usd_p:.2f}", f"{usd_v:.2%}")
    
    # Tendência média para exibição rápida
    var_media = (ny_v + lon_v + usd_v) / 3
    m4.metric("Tendência Geral", f"{(var_media*100):.2f}%")

    st.divider()
    
    # Criando 3 colunas para os tipos de café
    col_d, col_r, col_c = st.columns(3)

    # Variações específicas
    var_arabica = ny_v + usd_v
    var_conilon = lon_v + usd_v
    
    cor_ara = "#00FF00" if var_arabica >= 0 else "#FF4B4B"
    cor_con = "#00FF00" if var_conilon >= 0 else "#FF4B4B"

    # BEBIDA DURA (Segue NY)
    mudanca_dura = base_dura * var_arabica
    with col_d:
        st.subheader("☕ Bebida DURA")
        st.markdown(f"<h2 style='color:{cor_ara} !important; font-size: 35px;'>R$ {base_dura + mudanca_dura:.2f}</h2>", unsafe_allow_html=True)
        st.metric(label="Alvo Estimado (NY+USD)", value="", delta=float(round(mudanca_dura, 2)))

    # BEBIDA RIO (Segue NY)
    mudanca_rio = base_rio * var_arabica
    with col_r:
        st.subheader("☕ Bebida RIO")
        st.markdown(f"<h2 style='color:{cor_ara} !important; font-size: 35px;'>R$ {base_rio + mudanca_rio:.2f}</h2>", unsafe_allow_html=True)
        st.metric(label="Alvo Estimado (NY+USD)", value="", delta=float(round(mudanca_rio, 2)))

    # CAFÉ CONILON (Segue Londres)
    mudanca_conilon = base_conilon * var_conilon
    with col_c:
        st.subheader("☕ Café CONILON")
        st.markdown(f"<h2 style='color:{cor_con} !important; font-size: 35px;'>R$ {base_conilon + mudanca_conilon:.2f}</h2>", unsafe_allow_html=True)
        st.metric(label="Alvo Estimado (LON+USD)", value="", delta=float(round(mudanca_conilon, 2)))

st.divider()
with st.expander("🧐 Por que o Conilon usa uma Bolsa diferente?"):
    st.markdown("""
    O mercado mundial de café é dividido em dois grandes grupos:
    * **Arábica (Bebida Dura/Rio):** O preço é definido na Bolsa de Nova York (ICE).
    * **Robusta/Conilon:** O preço mundial de referência é definido na Bolsa de Londres. 
    
    Como o Espírito Santo é o maior produtor de Conilon do Brasil, este painel agora separa os cálculos para que a sua previsão seja muito mais próxima da realidade do que está acontecendo no mundo.
    """)

st.caption("Atualizado via CCCV e Yahoo Finance.")
