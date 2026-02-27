import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import base64
import os
import streamlit.components.v1 as components

# Configuração da página
st.set_page_config(page_title="Previsão Café ES", page_icon="☕", layout="wide")

# --- FUNÇÃO DE FUNDO E ESTILO ---
def add_bg_and_style(image_file):
    if os.path.exists(image_file):
        with open(image_file, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), url("data:image/jpg;base64,{encoded_string}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}
            /* Estilização global */
            h1, h2, h3, p, span, label, div {{
                color: white !important;
                text-shadow: 2px 2px 4px rgba(0,0,0,1) !important;
            }}
            /* Título Principal */
            .main-title {{
                text-align: center;
                font-size: 50px !important;
                font-weight: bold;
                margin-bottom: 20px;
                color: #F1C40F !important;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

add_bg_and_style('historia_do_cafe-968x660-1-968x560.jpg')

# --- TÍTULO PRINCIPAL NO TOPO ---
st.markdown('<h1 class="main-title">Previsao do Cafe ☕</h1>', unsafe_allow_html=True)

def buscar_dados_cccv():
    url = "https://www.cccv.org.br/cotacao/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        tabelas = pd.read_html(response.text)
        df = tabelas[0]
        dura_str = df.loc[df[0].str.contains("dura", case=False), 1].values[0]
        rio_str = df.loc[df[0].str.contains("rio", case=False), 1].values[0]
        dura = float(str(dura_str).replace('.', '').replace(',', '.'))
        rio = float(str(rio_str).replace('.', '').replace(',', '.'))
        return dura, rio
    except:
        return 1694.00, 1349.00 

def buscar_mercado():
    try:
        cafe_ny = yf.download("KC=F", period="5d", interval="1d", progress=False)
        dolar = yf.download("USDBRL=X", period="5d", interval="1d", progress=False)

        if isinstance(cafe_ny.columns, pd.MultiIndex):
            cafe_ny.columns = cafe_ny.columns.get_level_values(0)
        if isinstance(dolar.columns, pd.MultiIndex):
            dolar.columns = dolar.columns.get_level_values(0)

        df_ny = cafe_ny['Close'].dropna()
        df_usd = dolar['Close'].dropna()

        cot_ny = float(df_ny.iloc[-1])
        prev_ny = float(df_ny.iloc[-2])
        v_ny = (cot_ny / prev_ny) - 1

        cot_usd = float(df_usd.iloc[-1])
        prev_usd = float(df_usd.iloc[-2])
        v_usd = (cot_usd / prev_usd) - 1

        return cot_ny, v_ny, cot_usd, v_usd
    except Exception:
        return 0.0, 0.0, 0.0, 0.0

st.divider()

base_dura, base_rio = buscar_dados_cccv()
ny_p, ny_v, usd_p, usd_v = buscar_mercado()

if ny_p == 0:
    st.warning("Carregando dados da bolsa...")
else:
    var_total = ny_v + usd_v
    cor_tendencia = "#00FF00" if var_total >= 0 else "#FF0000"

    c1, c2, c3 = st.columns(3)
    c1.metric("Bolsa NY (Arábica)", f"{ny_p:.2f} pts", f"{ny_v:.2%}")
    c2.metric("Dólar Comercial", f"R$ {usd_p:.4f}", f"{usd_v:.2%}")
    c3.metric("Tendência Combinada", f"{(var_total*100):.2f}%")

    st.divider()
    col_d, col_r = st.columns(2)

    preco_final_dura = base_dura * (1 + var_total)
    mudanca_dura = preco_final_dura - base_dura
    
    with col_d:
        st.subheader("☕ Bebida DURA")
        st.markdown(f"<h2 style='color:{cor_tendencia} !important; font-size: 40px;'>R$ {preco_final_dura:.2f}</h2>", unsafe_allow_html=True)
        st.metric(label="Alvo Estimado", value="", delta=float(round(mudanca_dura, 2)), delta_color="normal")

    preco_final_rio = base_rio * (1 + var_total)
    mudanca_rio = preco_final_rio - base_rio
    
    with col_r:
        st.subheader("☕ Bebida RIO")
        st.markdown(f"<h2 style='color:{cor_tendencia} !important; font-size: 40px;'>R$ {preco_final_rio:.2f}</h2>", unsafe_allow_html=True)
        st.metric(label="Alvo Estimado", value="", delta=float(round(mudanca_rio, 2)), delta_color="normal")

    # --- NOVO: GRÁFICO DO TRADINGVIEW ---
    st.divider()
    st.subheader("📊 Gráfico em Tempo Real (Bolsa NY)")
    
    tradingview_widget = """
    <div class="tradingview-widget-container" style="height:500px; width:100%;">
      <div id="tradingview_cafe" style="height:calc(100% - 32px);width:100%;"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({
        "autosize": true,
        "symbol": "ICEUS:KC1!",
        "interval": "D",
        "timezone": "America/Sao_Paulo",
        "theme": "dark",
        "style": "1",
        "locale": "br",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "hide_side_toolbar": false,
        "allow_symbol_change": true,
        "container_id": "tradingview_cafe"
      });
      </script>
    </div>
    """
    components.html(tradingview_widget, height=500)

st.divider()
st.markdown("### 📖 Como funciona este Painel?")
st.write("Este site realiza uma simulação do impacto do mercado financeiro global no preço físico do café no Espírito Santo.")

exp_col1, exp_col2, exp_col3 = st.columns(3)
with exp_col1:
    st.markdown("**1. Preço Base (CCCV)**")
    st.write("Buscamos diariamente as cotações oficiais de Bebida Dura e Bebida Rio diretamente do site do CCCV.")
with exp_col2:
    st.markdown("**2. Variação Combinada**")
    st.write("O sistema monitora a oscilação da Bolsa de Nova York e do Dólar Comercial.")
with exp_col3:
    st.markdown("**3. Alvo Estimado**")
    st.write("Aplicamos a soma das variações sobre o preço base para prever a tendência.")

st.info("⚠️ **Aviso:** Este site está em fase de testes. Os valores são estimativas.")
st.markdown("<h3 style='text-align: center;'>Criado por: Marcos Gomes</h3>", unsafe_allow_html=True)
st.caption("Atualizado via CCCV, Yahoo Finance e TradingView.")
