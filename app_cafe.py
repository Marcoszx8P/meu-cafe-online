import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import base64
import os
from datetime import datetime

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Painel do Café ☕", page_icon="☕", layout="wide")

# --- 2. FUNÇÃO DE ESTILO E FUNDO ---
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
                text-align: center;
                font-size: 50px !important;
                font-weight: bold;
                margin-bottom: 10px;
                color: #F1C40F !important;
            }}
            [data-testid="stMetricValue"] {{ font-size: 28px !important; }}
            </style>
            """,
            unsafe_allow_html=True
        )

# --- 3. BUSCA DE DADOS FÍSICOS (CCCV) ---
def buscar_precos_fisicos():
    url = "https://www.cccv.org.br/cotacao/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        tabelas = pd.read_html(response.text)
        df = tabelas[0]
        
        # Captura valores limpando a pontuação brasileira
        dura = float(str(df.loc[df[0].str.contains("dura", case=False), 1].values[0]).replace('.', '').replace(',', '.'))
        rio = float(str(df.loc[df[0].str.contains("rio", case=False), 1].values[0]).replace('.', '').replace(',', '.'))
        conilon_mg = float(str(df.loc[df[0].str.contains("conilon", case=False), 1].values[0]).replace('.', '').replace(',', '.'))
        
        return dura, rio, conilon_mg
    except:
        # Valores de segurança caso o site do CCCV esteja fora do ar
        return 1690.00, 1330.00, 1440.00

# --- 4. BUSCA DE DADOS DE MERCADO (YAHOO FINANCE) ---
def buscar_mercado_financeiro():
    try:
        # Baixa 5 dias para garantir dados de fechamento no fim de semana
        ny = yf.download("KC=F", period="5d", interval="1d", progress=False)
        lon = yf.download("RC=F", period="5d", interval="1d", progress=False)
        usd = yf.download("USDBRL=X", period="5d", interval="1d", progress=False)

        def processar(df):
            precos = df['Close'].dropna()
            atual = float(precos.iloc[-1])
            anterior = float(precos.iloc[-2])
            variacao = (atual / anterior) - 1
            return atual, variacao

        p_ny, v_ny = processar(ny)
        p_lon, v_lon = processar(lon)
        p_usd, v_usd = processar(usd)

        return p_ny, v_ny, p_lon, v_lon, p_usd, v_usd
    except:
        return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

# --- 5. EXECUÇÃO DO PAINEL ---
add_bg_and_style('fundo_cafe_fazenda.avif')

st.markdown('<h1 class="main-title">Painel do Cafe ☕</h1>', unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center;'>Atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>", unsafe_allow_html=True)

# Coleta de dados
base_dura, base_rio, base_conilon = buscar_precos_fisicos()
ny_p, ny_v, lon_p, lon_v, usd_p, usd_v = buscar_mercado_financeiro()

if ny_p == 0:
    st.error("Erro ao carregar dados do Yahoo Finance. Tente atualizar a página.")
else:
    # CÁLCULO DAS DUAS TENDÊNCIAS PEDIDAS
    tend_arabica = ny_v + usd_v
    tend_conilon = lon_v + usd_v

    # BLOCO DE MÉTRICAS (NY, LONDRES, DÓLAR E AS DUAS TENDÊNCIAS)
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("NY (Arábica)", f"{ny_p:.2f} pts", f"{ny_v:.2%}")
    m2.metric("Londres (Conilon)", f"{lon_p:.0f} USD", f"{lon_v:.2%}")
    m3.metric("Dólar Comercial", f"R$ {usd_p:.2f}", f"{usd_v:.2%}")
    
    # Cores dinâmicas para as tendências
    cor_ara = "#00FF00" if tend_arabica >= 0 else "#FF4B4B"
    cor_con = "#00FF00" if tend_conilon >= 0 else "#FF4B4B"
    
    m4.metric("Tendência Arábica", f"{tend_arabica:.2%}")
    m5.metric("Tendência Conilon", f"{tend_conilon:.2%}")

    st.divider()

    # BLOCO DE PREÇOS FÍSICOS (DURA, RIO, CONILON MG)
    c1, c2, c3 = st.columns(3)

    with c1:
        st.subheader("☕ Bebida DURA")
        valor_dura = base_dura * (1 + tend_arabica)
        st.markdown(f"<h2 style='color:{cor_ara}; font-size: 42px;'>R$ {valor_dura:.2f}</h2>", unsafe_allow_html=True)
        st.caption(f"Base CCCV: R$ {base_dura:.2f}")

    with c2:
        st.subheader("☕ Bebida RIO")
        valor_rio = base_rio * (1 + tend_arabica)
        st.markdown(f"<h2 style='color:{cor_ara}; font-size: 42px;'>R$ {valor_rio:.2f}</h2>", unsafe_allow_html=True)
        st.caption(f"Base CCCV: R$ {base_rio:.2f}")

    with c3:
        st.subheader("☕ CONILON (MG)")
        valor_conilon = base_conilon * (1 + tend_conilon)
        st.markdown(f"<h2 style='color:{cor_con}; font-size: 42px;'>R$ {valor_conilon:.2f}</h2>", unsafe_allow_html=True)
        st.caption(f"Base Minas: R$ {base_conilon:.2f}")

st.divider()

# EXPLICAÇÃO PARA O PRODUTOR
with st.expander("🧐 Como funciona a somatória para chegar ao resultado?"):
    st.markdown(f"""
    O cálculo do **Alvo Estimado** é feito somando a variação da Bolsa com a variação do Dólar:
    
    1. **Para Arábica (Dura/Rio):** Somamos a oscilação de Nova York ({ny_v:.2%}) com o Dólar ({usd_v:.2%}). **Total: {tend_arabica:.2%}**.
    2. **Para Conilon:** Somamos a oscilação de Londres ({lon_v:.2%}) com o Dólar ({usd_v:.2%}). **Total: {tend_conilon:.2%}**.
    
    Aplicamos esse percentual sobre o preço físico de hoje para prever o comportamento do mercado.
    """)

st.markdown("<p style='text-align: center; opacity: 0.7;'>Criado por: Marcos Gomes | Fontes: CCCV e Yahoo Finance</p>", unsafe_allow_html=True)
