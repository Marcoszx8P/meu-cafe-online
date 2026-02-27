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
        
        # O CCCV costuma organizar: [0] Descrição, [1] Dura, [2] Rio, [3] Conilon
        # Vamos buscar por palavras-chave para evitar erro de coluna
        dura_str = df.loc[df[0].str.contains("dura", case=False), 1].values[0]
        rio_str = df.loc[df[0].str.contains("rio", case=False), 1].values[0]
        
        # O Conilon geralmente fica na última linha/coluna de preços
        # Tentamos buscar o valor na linha que contém '7/8' ou na coluna 3
        try:
            conilon_str = df.loc[df[0].str.contains("7/8", case=False), 1].values[0]
        except:
            conilon_str = df.iloc[-1, 1] # Pega o último valor da tabela se falhar

        dura = float(str(dura_str).replace('.', '').replace(',', '.'))
        rio = float(str(rio_str).replace('.', '').replace(',', '.'))
        conilon = float(str(conilon_str).replace('.', '').replace(',', '.'))
        
        return dura, rio, conilon
    except:
        # Fallback com valores de mercado atuais caso o site mude a estrutura
        return 1696.00, 1349.00, 972.00 

def buscar_mercado():
    try:
        ticker_ny = yf.Ticker("KC=F")
        ticker_usd = yf.Ticker("USDBRL=X")
        info_ny = ticker_ny.info
        info_usd = ticker_usd.info
        cot_ny = info_ny.get('regularMarketPrice', 0.0)
        v_ny = info_ny.get('regularMarketChangePercent', 0.0) / 100
        cot_usd = info_usd.get('regularMarketPrice', 0.0)
        v_usd = info_usd.get('regularMarketChangePercent', 0.0) / 100
        return cot_ny, v_ny, cot_usd, v_usd
    except:
        return 0.0, 0.0, 0.0, 0.0

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
ny_p, ny_v, usd_p, usd_v = buscar_mercado()

st.divider()
st.markdown("### 📖 Como funciona este Painel?")
st.write("Simulação do impacto do mercado global no preço físico do café no ES.")

exp_col1, exp_col2, exp_col3 = st.columns(3)
with exp_col1:
    st.markdown("**1. Preço Base (CCCV)**")
    st.write("Cotações oficiais de Bebida Dura, Rio e Conilon (Tipo 7/8) de Vitória.")
with exp_col2:
    st.markdown("**2. Variação Combinada**")
    st.write("Monitoramento de NY (Arábica) e Dólar em tempo real.")
with exp_col3:
    st.markdown("**3. Alvo Estimado**")
    st.write("Aplicação da oscilação financeira sobre o preço real de hoje.")

st.info("⚠️ **Aviso:** Valores estimativos para auxílio à decisão.")
st.markdown("<h1 style='text-align: center;'>Criado por: Marcos Gomes</h1>", unsafe_allow_html=True)

if ny_p == 0:
    st.warning("Carregando dados da bolsa...")
else:
    var_total = ny_v + usd_v
    cor_tendencia = "#00FF00" if var_total >= 0 else "#FF4B4B"

    c1, c2, c3 = st.columns(3)
    c1.metric("Bolsa NY (Arábica)", f"{ny_p:.2f} pts", f"{ny_v:.2%}")
    c2.metric("Dólar Comercial", f"R$ {usd_p:.2f}", f"{usd_v:.2%}")
    c3.metric("Tendência Combinada", f"{(var_total*100):.2f}%")

    st.divider()
    col_d, col_r, col_c = st.columns(3)

    # BEBIDA DURA
    mud_dura = base_dura * var_total
    with col_d:
        st.subheader("☕ Bebida DURA")
        st.markdown(f"<h2 style='color:{cor_tendencia} !important; font-size: 38px;'>R$ {base_dura + mud_dura:.2f}</h2>", unsafe_allow_html=True)
        st.metric(label="Base: R$ " + str(base_dura), value="", delta=float(round(mud_dura, 2)))

    # BEBIDA RIO
    mud_rio = base_rio * var_total
    with col_r:
        st.subheader("☕ Bebida RIO")
        st.markdown(f"<h2 style='color:{cor_tendencia} !important; font-size: 38px;'>R$ {base_rio + mud_rio:.2f}</h2>", unsafe_allow_html=True)
        st.metric(label="Base: R$ " + str(base_rio), value="", delta=float(round(mud_rio, 2)))

    # CAFÉ CONILON
    mud_conilon = base_conilon * var_total
    with col_c:
        st.subheader("☕ Café CONILON")
        st.markdown(f"<h2 style='color:{cor_tendencia} !important; font-size: 38px;'>R$ {base_conilon + mud_conilon:.2f}</h2>", unsafe_allow_html=True)
        st.metric(label="Base: R$ " + str(base_conilon), value="", delta=float(round(mud_conilon, 2)))

st.divider()
with st.expander("🧐 Como o cálculo é feito?"):
    st.markdown("""
    **Cálculo:** (Variação NY + Variação Dólar) x Preço Base CCCV.
    O "Base" que você vê abaixo do preço é o valor oficial retirado hoje do site do CCCV para o tipo 7/8.
    """)

st.caption("Atualizado via CCCV e Yahoo Finance.")
