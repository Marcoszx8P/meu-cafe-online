import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import base64

# Configuração da página
st.set_page_config(page_title="Previsão Café ES", page_icon="☕", layout="wide")

# --- ADIÇÃO: FUNÇÃO DA IMAGEM ---
def add_bg_from_local(image_file):
    with open(image_file, "rb") as f:
        encoded_string = base64.b64encode(f.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("data:image/jpg;base64,{encoded_string}");
            background-size: cover;
        }}
        /* Garante que o texto original apareça sobre o fundo */
        h1, h2, h3, p, span, label, .stMetric {{ color: white !important; }}
        </style>
        """,
        unsafe_allow_html=True
    )

try:
    add_bg_from_local('historia_do_cafe-968x660-1-968x560.jpg')
except:
    pass
# --- FIM DA ADIÇÃO ---

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
        
        cot_ny = float(cafe_ny['Close'].iloc[-1])
        v_ny = (cot_ny / float(cafe_ny['Close'].iloc[-2])) - 1
        
        cot_usd = float(dolar['Close'].iloc[-1])
        v_usd = (cot_usd / float(dolar['Close'].iloc[-2])) - 1
        
        return cot_ny, v_ny, cot_usd, v_usd
    except:
        return 0.0, 0.0, 0.0, 0.0

st.divider()

st.markdown("### 📖 Como funciona este Monitor?")
st.write("""
Este site realiza uma simulação do impacto do mercado financeiro global no preço físico do café no Espírito Santo. 
A lógica funciona em três etapas principais:
""")

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

st.info("⚠️ **Aviso de Versão Beta:** Este site está em fase de testes. Os valores são estimativas matemáticas para auxiliar na tomada de decisão e não garantem o preço final praticado pelas cooperativas.")

st.markdown("<br><br>", unsafe_allow_html=True) 
st.markdown("<h1 style='text-align: center;'>Criado por: Marcos Gomes</h1>", unsafe_allow_html=True)

base_dura, base_rio = buscar_dados_cccv()
ny_p, ny_v, usd_p, usd_v = buscar_mercado()

if ny_p == 0:
    st.warning("Carregando dados da bolsa...")
else:
    var_total = ny_v + usd_v
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Bolsa NY (Arábica)", f"{ny_p:.2f} pts", f"{ny_v:.2%}")
    c2.metric("Dólar Comercial", f"R$ {usd_p:.2f}", f"{usd_v:.2%}")
    c3.metric("Tendência Combinada", f"{(var_total*100):.2f}%")

    st.divider()
    col_d, col_r = st.columns(2)

    mudanca_dura = base_dura * var_total
    with col_d:
        st.subheader("☕ Bebida DURA")
        st.metric(
            label="Alvo Estimado", 
            value=f"R$ {base_dura + mudanca_dura:.2f}", 
            delta=float(round(mudanca_dura, 2)),
            delta_color="normal"
        )

    mudanca_rio = base_rio * var_total
    with col_r:
        st.subheader("☕ Bebida RIO")
        st.metric(
            label="Alvo Estimado", 
            value=f"R$ {base_rio + mudanca_rio:.2f}", 
            delta=float(round(mudanca_rio, 2)),
            delta_color="normal"
        )

st.divider()
st.caption("Atualizado via CCCV e Yahoo Finance.")
