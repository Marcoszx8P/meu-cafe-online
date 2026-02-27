import streamlit as st
import pandas as pd
import yfinance as yf
import requests

# 1. Configuração da página
st.set_page_config(page_title="Previsão Café ES", page_icon="☕", layout="wide")

# 2. Funções de captura de dados
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
        return 1694.00, 1349.00 # Valores de segurança

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

# 3. Cabeçalho e Resultados
st.title("📊 Monitor de Tendência do Café - ES")

base_dura, base_rio = buscar_dados_cccv()
ny_p, ny_v, usd_p, usd_v = buscar_mercado()

if ny_p == 0:
    st.warning("Carregando dados da bolsa...")
else:
    var_total = ny_v + usd_v
    
    # Painel Principal
    c1, c2, c3 = st.columns(3)
    c1.metric("Bolsa NY (Arábica)", f"{ny_p:.2f} pts", f"{ny_v:.2%}", delta_color="normal")
    c2.metric("Dólar Comercial", f"R$ {usd_p:.2f}", f"{usd_v:.2%}", delta_color="normal")
    c3.metric("Tendência Combinada", f"{(var_total*100):.2f}%")

    st.divider()
    col_d, col_r = st.columns(2)

    # Bebida DURA
    mudanca_dura = base_dura * var_total
    with col_d:
        st.subheader("☕ Bebida DURA")
        st.metric(
            label="Alvo Estimado", 
            value=f"R$ {base_dura + mudanca_dura:.2f}", 
            delta=float(round(mudanca_dura, 2)),
            delta_color="normal"
        )

    # Bebida RIO
    mudanca_rio = base_rio * var_total
    with col_r:
        st.subheader("☕ Bebida RIO")
        st.metric(
            label="Alvo Estimado", 
            value=f"R$ {base_rio + mudanca_rio:.2f}", 
            delta=float(round(mudanca_rio, 2)),
            delta_color="normal"
        )

# 4. Seção Informativa (Parte de baixo)
st.divider()
st.markdown("### 📖 Como funciona este Monitor?")
st.write("Este site simula o impacto do mercado financeiro global no preço físico do café no Espírito Santo.")

exp_col1, exp_col2, exp_col3 = st.columns(3)
with exp_col1:
    st.markdown("**1. Preço Base (CCCV)**")
    st.write("Buscamos as cotações oficiais de Vitória.")

with exp_col2:
    st.markdown("**2. Variação Combinada**")
    st.write("Monitoramos a oscilação da Bolsa de NY e do Dólar em tempo real.")

with exp_col3:
    st.markdown("**3. Alvo Estimado**")
    st.write("Previsão baseada na soma das variações sobre o preço base.")

# --- BLOCO CORRIGIDO DO CCCV ---
st.info("🕒 **Nota sobre o fechamento:** O CCCV publica os valores exatos de fechamento do dia entre **16:00 e 17:00**. Antes desse horário, o
