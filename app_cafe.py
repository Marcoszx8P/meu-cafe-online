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
        
        dura_str = df.loc[df[0].str.contains("dura", case=False), 1].values[0]
        rio_str = df.loc[df[0].str.contains("rio", case=False), 1].values[0]
        
        try:
            conilon_str = df.loc[df[0].str.contains("7/8", case=False), 1].values[0]
        except:
            conilon_str = df.iloc[-1, 1]

        dura = float(str(dura_str).replace('.', '').replace(',', '.'))
        rio = float(str(rio_str).replace('.', '').replace(',', '.'))
        conilon = float(str(conilon_str).replace('.', '').replace(',', '.'))
        
        return dura, rio, conilon
    except:
        return 1696.00, 1349.00, 972.00 

def buscar_mercado():
    try:
        # Tickers: KC=F (NY/Arábica), RC=F (Londres/Conilon), USDBRL=X (Dólar)
        ticker_ny = yf.Ticker("KC=F")
        ticker_lon = yf.Ticker("RC=F")
        ticker_usd = yf.Ticker("USDBRL=X")
        
        # Coleta NY
        v_ny = ticker_ny.info.get('regularMarketChangePercent', 0.0) / 100
        p_ny = ticker_ny.info.get('regularMarketPrice', 0.0)
        
        # Coleta Londres
        v_lon = ticker_lon.info.get('regularMarketChangePercent', 0.0) / 100
        p_lon = ticker_lon.info.get('regularMarketPrice', 0.0)
        
        # Coleta Dólar
        v_usd = ticker_usd.info.get('regularMarketChangePercent', 0.0) / 100
        p_usd = ticker_usd.info.get('regularMarketPrice', 0.0)
        
        return p_ny, v_ny, p_lon, v_lon, p_usd, v_usd
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

base_dura, base_rio, base_conilon = buscar_dados_cccv()
ny_p, ny_v, lon_p, lon_v, usd_p, usd_v = buscar_mercado()

st.divider()
st.markdown("### 📖 Como funciona este Painel?")
st.write("Simulação do impacto do mercado global no preço físico do café no ES.")

exp_col1, exp_col2, exp_col3 = st.columns(3)
with exp_col1:
    st.markdown("**1. Preço Base (CCCV)**")
    st.write("Cotações oficiais de Bebida Dura, Rio e Conilon (Tipo 7/8) de Vitória.")
with exp_col2:
    st.markdown("**2. Inteligência por Tipo**")
    st.write("O Arábica segue a Bolsa de **Nova York**, enquanto o Conilon segue a Bolsa de **Londres**.")
with exp_col3:
    st.markdown("**3. Alvo Estimado**")
    st.write("Somamos a variação da Bolsa respectiva + Dólar sobre o preço base do dia.")

st.info("⚠️ **Aviso:** Valores estimativos para auxílio à decisão.")
st.markdown("<h1 style='text-align: center;'>Criado por: Marcos Gomes</h1>", unsafe_allow_html=True)

if ny_p == 0 or lon_p == 0:
    st.warning("Carregando dados das bolsas mundiais...")
else:
    # Indicadores principais
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Bolsa NY (Arábica)", f"{ny_p:.2f} pts", f"{ny_v:.2%}")
    c2.metric("Bolsa Londres (Conilon)", f"{lon_p:.2f} pts", f"{lon_v:.2%}")
    c3.metric("Dólar Comercial", f"R$ {usd_p:.2f}", f"{usd_v:.2%}")
    
    # Tendência combinada (média simples apenas para o resumo)
    tendencia_geral = (ny_v + lon_v + usd_v) / 2
    c4.metric("Tendência Média", f"{(tendencia_geral*100):.2f}%")

    st.divider()
    col_d, col_r, col_c = st.columns(3)

    # CÁLCULOS ESPECÍFICOS
    var_arabica = ny_v + usd_v
    var_conilon = lon_v + usd_v
    
    cor_ara = "#00FF00" if var_arabica >= 0 else "#FF4B4B"
    cor_con = "#00FF00" if var_conilon >= 0 else "#FF4B4B"

    # BEBIDA DURA (Baseado em NY)
    mud_dura = base_dura * var_arabica
    with col_d:
        st.subheader("☕ Bebida DURA")
        st.markdown(f"<h2 style='color:{cor_ara} !important; font-size: 38px;'>R$ {base_dura + mud_dura:.2f}</h2>", unsafe_allow_html=True)
        st.metric(label="Base: R$ " + str(base_dura), value="", delta=float(round(mud_dura, 2)))

    # BEBIDA RIO (Baseado em NY)
    mud_rio = base_rio * var_arabica
    with col_r:
        st.subheader("☕ Bebida RIO")
        st.markdown(f"<h2 style='color:{cor_ara} !important; font-size: 38px;'>R$ {base_rio + mud_rio:.2f}</h2>", unsafe_allow_html=True)
        st.metric(label="Base: R$ " + str(base_rio), value="", delta=float(round(mud_rio, 2)))

    # CAFÉ CONILON (Baseado em LONDRES)
    mud_conilon = base_conilon * var_conilon
    with col_c:
        st.subheader("☕ Café CONILON")
        st.markdown(f"<h2 style='color:{cor_con} !important; font-size: 38px;'>R$ {base_conilon + mud_conilon:.2f}</h2>", unsafe_allow_html=True)
        st.metric(label="Base: R$ " + str(base_conilon), value="", delta=float(round(mud_conilon, 2)))

st.divider()
with st.expander("🧐 Como o cálculo é feito agora?"):
    st.markdown("""
    **Agora o painel é mais preciso:**
    - **Arábica (Dura/Rio):** Calculado usando (Variação da Bolsa de NY + Variação do Dólar).
    - **Conilon:** Calculado usando (Variação da Bolsa de Londres + Variação do Dólar).
    
    Isso é necessário porque o Conilon não segue Nova York, mas sim o mercado europeu de Robustas em Londres.
    """)

st.caption("Atualizado via CCCV, Yahoo Finance (NY e Londres).")
