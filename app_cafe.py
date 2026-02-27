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
        # ACRÉSCIMO CONILON
        conilon_str = df.loc[df[0].str.contains("7/8", case=False), 1].values[0]
        
        dura = float(str(dura_str).replace('.', '').replace(',', '.'))
        rio = float(str(rio_str).replace('.', '').replace(',', '.'))
        conilon = float(str(conilon_str).replace('.', '').replace(',', '.'))
        return dura, rio, conilon
    except:
        return 1694.00, 1349.00, 970.00 

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
            /* TEXTOS EM BRANCO PURO COM SOMBRA */
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

# Chamando as funções
base_dura, base_rio, base_conilon = buscar_dados_cccv()
ny_p, ny_v, usd_p, usd_v = buscar_mercado()

st.divider()
st.markdown("### 📖 Como funciona este Painel?")
st.write("Este site realiza uma simulação do impacto do mercado financeiro global no preço físico do café no Espírito Santo.")

exp_col1, exp_col2, exp_col3 = st.columns(3)
with exp_col1:
    st.markdown("**1. Preço Base (CCCV)**")
    st.write("Buscamos diariamente as cotações oficiais de Bebida Dura e Bebida Rio diretamente do site do CCCV em Vitória.")
with exp_col2:
    st.markdown("**2. Variação Combinada**")
    st.write("O sistema monitora em tempo real a oscilação da Bolsa de Nova York (Arábica) e do Dólar Comercial.")
with exp_col3:
    st.markdown("**3. Alvo Estimado**")
    st.write("Aplicamos a soma das variações de NY e do Dólar sobre o preço base para prever a tendência do mercado físico.")

st.info("⚠️ **Aviso:** Este site está em fase de testes. Os valores são estimativas matemáticas para auxiliar na tomada de decisão e não garantem o preço final praticado pelas cooperativas.")
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
    
    # ACRÉSCIMO DO PAINEL CONILON LOGO ABAIXO DOS INDICADORES
    mudanca_conilon = base_conilon * var_total
    st.subheader("☕ Café CONILON (Tipo 7/8)")
    st.markdown(f"<h2 style='color:{cor_tendencia} !important; font-size: 40px;'>R$ {base_conilon + mudanca_conilon:.2f}</h2>", unsafe_allow_html=True)
    st.metric(label="Alvo Estimado Conilon", value="", delta=float(round(mudanca_conilon, 2)), delta_color="normal")

    st.divider()
    col_d, col_r = st.columns(2)

    # BEBIDA DURA
    mudanca_dura = base_dura * var_total
    with col_d:
        st.subheader("☕ Bebida DURA")
        st.markdown(f"<h2 style='color:{cor_tendencia} !important; font-size: 40px;'>R$ {base_dura + mudanca_dura:.2f}</h2>", unsafe_allow_html=True)
        st.metric(label="Alvo Estimado", value="", delta=float(round(mudanca_dura, 2)), delta_color="normal")

    # BEBIDA RIO
    mudanca_rio = base_rio * var_total
    with col_r:
        st.subheader("☕ Bebida RIO")
        st.markdown(f"<h2 style='color:{cor_tendencia} !important; font-size: 40px;'>R$ {base_rio + mudanca_rio:.2f}</h2>", unsafe_allow_html=True)
        st.metric(label="Alvo Estimado", value="", delta=float(round(mudanca_rio, 2)), delta_color="normal")

st.divider()
# --- OPÇÃO PARA O PRODUTOR ENTENDER (FINAL DO SITE) ---
st.divider()
with st.expander("🧐 Produtor, clique aqui para entender como chegamos a esses valores"):
    st.markdown("""
    ### A Matemática do Mercado
    O preço do café no Espírito Santo não muda ao acaso. Ele é o reflexo de duas forças globais:
    
    1. **Bolsa de Nova York (ICE):** É onde o mundo define o valor do café Arábica. Se lá o preço sobe, o mercado aqui tende a acompanhar.
    2. **Dólar:** Como o café é uma exportação, o produtor recebe o valor convertido. Se o dólar sobe, o seu café vale mais em Reais.
    
    **Como o cálculo é feito?**
    Nós somamos as duas variações do dia. Por exemplo:
    * Se a Bolsa de NY subir **1%** e o Dólar subir **1%**, a tendência é de uma alta de **2%** no preço físico.
    * Se a Bolsa subir **1%** mas o Dólar cair **1%**, o preço tende a ficar **estável**.
    
    **Resultado Final:**
    Pegamos o preço oficial de hoje do **CCCV (Vitória)** e aplicamos essa porcentagem. O "Alvo Estimado" mostra qual seria o preço justo caso a cooperativa seguisse exatamente a movimentação do mercado financeiro agora.
    """)

st.caption("Atualizado via CCCV e Yahoo Finance.")
