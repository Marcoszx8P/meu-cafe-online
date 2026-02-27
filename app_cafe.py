import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import base64
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Previsão Café ES", page_icon="☕", layout="wide")

# --- 2. FUNÇÕES DE BUSCA ---
def buscar_dados_cccv():
    url = "https://www.cccv.org.br/cotacao/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        # Busca Bebida Dura, Rio e Conilon no site oficial
        response = requests.get(url, headers=headers, timeout=10)
        tabelas = pd.read_html(response.text)
        df = tabelas[0]
        dura_str = df.loc[df[0].str.contains("dura", case=False), 1].values[0]
        rio_str = df.loc[df[0].str.contains("rio", case=False), 1].values[0]
        conilon_str = df.loc[df[0].str.contains("conilon", case=False), 1].values[0]
        
        dura = float(str(dura_str).replace('.', '').replace(',', '.'))
        rio = float(str(rio_str).replace('.', '').replace(',', '.'))
        conilon = float(str(conilon_str).replace('.', '').replace(',', '.'))
        return dura, rio, conilon
    except:
        return 1694.00, 1349.00, 1050.00 

def buscar_londres_investing():
    """Busca dados diretamente do Investing.com conforme solicitado"""
    url = "https://br.investing.com/commodities/london-coffee"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Captura o preço e a variação percentual
        preco_texto = soup.find("div", {"data-test": "instrument-price-last"}).text
        var_texto = soup.find("span", {"data-test": "instrument-price-change-percent"}).text
        
        preco = float(preco_texto.replace('.', '').replace(',', '.'))
        var = float(var_texto.replace('(', '').replace(')', '').replace('%', '').replace(',', '.')) / 100
        return preco, var
    except:
        return 0.0, 0.0

def buscar_mercado():
    try:
        ticker_ny = yf.Ticker("KC=F")
        ticker_usd = yf.Ticker("USDBRL=X")
        
        cot_ny = ticker_ny.info.get('regularMarketPrice', 0.0)
        v_ny = ticker_ny.info.get('regularMarketChangePercent', 0.0) / 100
        
        cot_usd = ticker_usd.info.get('regularMarketPrice', 0.0)
        v_usd = ticker_usd.info.get('regularMarketChangePercent', 0.0) / 100
        
        # Londres vindo do Investing.com
        cot_ld, v_ld = buscar_londres_investing()
        
        return cot_ny, v_ny, cot_ld, v_ld, cot_usd, v_usd
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
        st.sidebar.error(f"Erro: O arquivo '{image_file}' não foi encontrado na pasta.")

# --- 4. EXECUÇÃO DO PAINEL ---
add_bg_and_style('fundo_cafe_fazenda.avif')

st.markdown('<h1 class="main-title">Previsao do Cafe ☕</h1>', unsafe_allow_html=True)

base_dura, base_rio, base_conilon = buscar_dados_cccv()
ny_p, ny_v, ld_p, ld_v, usd_p, usd_v = buscar_mercado()

st.divider()
st.markdown("### 📖 Como funciona este Painel?")
st.write("Este site realiza uma simulação do impacto do mercado financeiro global no preço físico do café no Espírito Santo.")

exp_col1, exp_col2, exp_col3 = st.columns(3)
with exp_col1:
    st.markdown("**1. Preço Base (CCCV)**")
    st.write("Buscamos diariamente as cotações oficiais de Bebida Dura, Rio e Conilon diretamente do site do CCCV em Vitória.")
with exp_col2:
    st.markdown("**2. Variação Combinada**")
    st.write("O sistema monitora a oscilação da Bolsa de Nova York (Arábica), Londres (Conilon via Investing.com) e do Dólar Comercial.")
with exp_col3:
    st.markdown("**3. Alvo Estimado**")
    st.write("Aplicamos a soma das variações de NY/Londres e do Dólar sobre o preço base para prever a tendência do mercado físico.")

st.info("⚠️ **Aviso:** Este site está em fase de testes.")
st.markdown("<h1 style='text-align: center;'>Criado por: Marcos Gomes</h1>", unsafe_allow_html=True)

if ny_p == 0:
    st.warning("Carregando dados da bolsa...")
else:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Bolsa NY (Arábica)", f"{ny_p:.2f} pts", f"{ny_v:.2%}")
    # Exibição de Londres limpa, igual ao Investing.com
    c2.metric("Londres (Investing)", f"{ld_p:.0f}", f"{ld_v:.2%}") 
    c3.metric("Dólar Comercial", f"R$ {usd_p:.2f}", f"{usd_v:.2%}")
    
    var_total_arabica = ny_v + usd_v
    var_total_conilon = ld_v + usd_v
    
    st.divider()
    col_d, col_r, col_c = st.columns(3)

    # BEBIDA DURA (Base NY)
    mudanca_dura = base_dura * var_total_arabica
    cor_dura = "#00FF00" if var_total_arabica >= 0 else "#FF4B4B"
    with col_d:
        st.subheader("☕ Bebida DURA")
        st.markdown(f"<h2 style='color:{cor_dura} !important; font-size: 35px;'>R$ {base_dura + mudanca_dura:.2f}</h2>", unsafe_allow_html=True)
        st.metric(label="Alvo Estimado", value="", delta=float(round(mudanca_dura, 2)))

    # BEBIDA RIO (Base NY)
    mudanca_rio = base_rio * var_total_arabica
    cor_rio = "#00FF00" if var_total_arabica >= 0 else "#FF4B4B"
    with col_r:
        st.subheader("☕ Bebida RIO")
        st.markdown(f"<h2 style='color:{cor_rio} !important; font-size: 35px;'>R$ {base_rio + mudanca_rio:.2f}</h2>", unsafe_allow_html=True)
        st.metric(label="Alvo Estimado", value="", delta=float(round(mudanca_rio, 2)))

    # CONILON (Base LONDRES/INVESTING)
    mudanca_conilon = base_conilon * var_total_conilon
    cor_conilon = "#00FF00" if var_total_conilon >= 0 else "#FF4B4B"
    with col_c:
        st.subheader("☕ CONILON Type 7")
        st.markdown(f"<h2 style='color:{cor_conilon} !important; font-size: 35px;'>R$ {base_conilon + mudanca_conilon:.2f}</h2>", unsafe_allow_html=True)
        st.metric(label="Alvo Estimado", value="", delta=float(round(mudanca_conilon, 2)))

st.divider()
with st.expander("🧐 Produtor, clique aqui para entender como chegamos a esses valores"):
    st.markdown("""
    ### A Matemática do Mercado
    * **Arábica (Dura/Rio):** Segue a Bolsa de Nova York + Dólar.
    * **Conilon:** Segue a Bolsa de Londres (Robusta via Investing.com) + Dólar.
    """)

st.caption("Fontes: CCCV Vitória, Investing.com (Londres) e Yahoo Finance (NY/Dólar).")
