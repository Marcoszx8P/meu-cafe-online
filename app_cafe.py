import streamlit as st
import pandas as pd
import yfinance as yf

# Configuração da página do site
st.set_page_config(page_title="Previsão Café ES", page_icon="☕", layout="wide")

# --- FUNÇÃO PARA BUSCAR PREÇOS NO CCCV ---
def buscar_dados_cccv():
    try:
        url = "https://www.cccv.org.br/cotacao/"
        # O pandas lê a tabela direto do site
        tabelas = pd.read_html(url)
        df = tabelas[0]
        
        # Busca os valores nas linhas corretas
        preco_dura_str = df.loc[df[0].str.contains("dura", case=False), 1].values[0]
        preco_rio_str = df.loc[df[0].str.contains("rio", case=False), 1].values[0]
        
        # Converte o texto "1.694,00" para o número 1694.00
        dura = float(preco_dura_str.replace('.', '').replace(',', '.'))
        rio = float(preco_rio_str.replace('.', '').replace(',', '.'))
        return dura, rio
    except Exception as e:
        st.error(f"Erro ao acessar o site do CCCV: {e}")
        return 1694.00, 1349.00  # Valores reserva caso o site caia

# --- FUNÇÃO PARA BUSCAR BOLSA E DÓLAR ---
def buscar_mercado_financeiro():
    # KC=F é o café Arábica na Bolsa de NY
    cafe_ny = yf.Ticker("KC=F").history(period="2d")
    # USDBRL=X é o dólar comercial
    dolar = yf.Ticker("USDBRL=X").history(period="2d")
    
    var_ny = (cafe_ny['Close'].iloc[-1] / cafe_ny['Close'].iloc[-2]) - 1
    var_usd = (dolar['Close'].iloc[-1] / dolar['Close'].iloc[-2]) - 1
    
    return cafe_ny['Close'].iloc[-1], var_ny, dolar['Close'].iloc[-1], var_usd

# --- INTERFACE DO SITE ---
st.title("📊 Monitor de Tendência do Café - Espírito Santo")
st.markdown(f"Dados extraídos automaticamente do **CCCV**, **Bolsa de NY** e **Dólar**.")

# Executa as buscas
preco_dura_base, preco_rio_base = buscar_dados_cccv()
cotacao_ny, var_ny, cotacao_usd, var_usd = buscar_mercado_financeiro()

# Cálculo da variação combinada
variacao_total = var_ny + var_usd

# Colunas de Indicadores Financeiros
col1, col2, col3 = st.columns(3)
col1.metric("Bolsa NY (Arábica)", f"{cotacao_ny:.2f} pts", f"{var_ny:.2%}")
col2.metric("Dólar Comercial", f"R$ {cotacao_usd:.2f}", f"{var_usd:.2%}")
col3.metric("Tendência Combinada", f"{(variacao_total*100):.2f}%", delta_color="normal")

st.divider()

# --- ÁREA DE CÁLCULO E PREVISÃO ---
col_dura, col_rio = st.columns(2)

# Cálculos para Bebida Dura
mudanca_dura = preco_dura_base * variacao_total
previsao_dura = preco_dura_base + mudanca_dura

with col_dura:
    st.subheader("☕ Bebida DURA")
    st.info(f"Preço Base (CCCV): **R$ {preco_dura_base:.2f}**")
    if mudanca_dura > 0:
        st.success(f"**Previsão de Alta: + R$ {mudanca_dura:.2f}**")
    else:
        st.error(f"**Previsão de Baixa: R$ {mudanca_dura:.2f}**")
    st.metric("Alvo Estimado", f"R$ {previsao_dura:.2f}")

# Cálculos para Bebida Rio
mudanca_rio = preco_rio_base * variacao_total
previsao_rio = preco_rio_base + mudanca_rio

with col_rio:
    st.subheader("☕ Bebida RIO")
    st.info(f"Preço Base (CCCV): **R$ {preco_rio_base:.2f}**")
    if mudanca_rio > 0:
        st.success(f"**Previsão de Alta: + R$ {mudanca_rio:.2f}**")
    else:
        st.error(f"**Previsão de Baixa: R$ {mudanca_rio:.2f}**")
    st.metric("Alvo Estimado", f"R$ {previsao_rio:.2f}")

st.divider()
st.caption("Nota: Este cálculo é uma estimativa baseada na variação do mercado financeiro. O preço final depende da sua cooperativa local.")
