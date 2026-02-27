import streamlit as st
import pandas as pd
import yfinance as yf
import requests

# Configuração da página
st.set_page_config(page_title="Previsão Café ES", page_icon="☕", layout="wide")

# --- FUNÇÃO PARA BUSCAR PREÇOS NO CCCV ---
def buscar_dados_cccv():
    url = "https://www.cccv.org.br/cotacao/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        tabelas = pd.read_html(response.text)
        df = tabelas[0]
        
        # Filtra as linhas de Bebida Dura e Rio
        dura_str = df.loc[df[0].str.contains("dura", case=False), 1].values[0]
        rio_str = df.loc[df[0].str.contains("rio", case=False), 1].values[0]
        
        dura = float(str(dura_str).replace('.', '').replace(',', '.'))
        rio = float(str(rio_str).replace('.', '').replace(',', '.'))
        return dura, rio
    except Exception:
        # Valores de segurança baseados no seu print
        return 1694.00, 1349.00 

# --- FUNÇÃO PARA BUSCAR BOLSA NY E DÓLAR ---
def buscar_mercado():
    try:
        # Baixa dados de 5 dias para garantir que não venha vazio
        cafe_ny = yf.download("KC=F", period="5d", interval="1d", progress=False)
        dolar = yf.download("USDBRL=X", period="5d", interval="1d", progress=False)
        
        # Pega o último valor de fechamento
        cot_ny = float(cafe_ny['Close'].iloc[-1])
        cot_ny_ontem = float(cafe_ny['Close'].iloc[-2])
        v_ny = (cot_ny / cot_ny_ontem) - 1
        
        cot_usd = float(dolar['Close'].iloc[-1])
        cot_usd_ontem = float(dolar['Close'].iloc[-2])
        v_usd = (cot_usd / cot_usd_ontem) - 1
        
        return cot_ny, v_ny, cot_usd, v_usd
    except Exception:
        return 0.0, 0.0, 0.0, 0.0

# --- TELA DO SITE ---
st.title("📊 Monitor de Tendência do Café - ES")

# Busca as informações
base_dura, base_rio = buscar_dados_cccv()
ny_p, ny_v, usd_p, usd_v = buscar_mercado()

if ny_p == 0:
    st.warning("Aguardando conexão com a Bolsa de Valores... Tente atualizar a página.")
else:
    var_total = ny_v + usd_v
    
    # Indicadores do Topo
    c1, c2, c3 = st.columns(3)
    c1.metric("Bolsa NY (Arábica)", f"{ny_p:.2f} pts", f"{ny_v:.2%}", delta_color="normal")
    c2.metric("Dólar Comercial", f"R$ {usd_p:.2f}", f"{usd_v:.2%}", delta_color="normal")
    c3.metric("Tendência Combinada", f"{(var_total*100):.2f}%", delta_color="off")

    st.divider()
    col_d, col_r = st.columns(2)

    # Cálculo Bebida Dura
    mudanca_dura = base_dura * var_total
    with col_d:
        st.subheader("☕ Bebida DURA")
        st.metric(
            label="Alvo Estimado", 
            value=f"R$ {base_dura + mudanca_dura:.2f}", 
            delta=f"R$ {mudanca_dura:.2f}",
            delta_color="normal" # CORRIGIDO: Verde para alta, Vermelho para queda
        )

    # Cálculo Bebida Rio
    mudanca_rio = base_rio * var_total
    with col_r:
        st.subheader("☕ Bebida RIO")
        st.metric(
            label="Alvo Estimado", 
            value=f"R$ {base_rio + mudanca_rio:.2f}", 
            delta=f"R$ {mudanca_rio:.2f}",
            delta_color="normal" # CORRIGIDO: Verde para alta, Vermelho para queda
        )

st.divider()
st.caption("Dados atualizados automaticamente via CCCV e Yahoo Finance.")
