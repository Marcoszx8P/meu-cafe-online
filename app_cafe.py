import streamlit as st
import pandas as pd
import yfinance as yf
import requests

# Configuração da página
st.set_page_config(page_title="Previsão Café ES", page_icon="☕", layout="wide")

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
        
        # Garantindo que pegamos números puros para o cálculo
        cot_ny = float(cafe_ny['Close'].iloc[-1])
        v_ny = (cot_ny / float(cafe_ny['Close'].iloc[-2])) - 1
        
        cot_usd = float(dolar['Close'].iloc[-1])
        v_usd = (cot_usd / float(dolar['Close'].iloc[-2])) - 1
        
        return cot_ny, v_ny, cot_usd, v_usd
    except:
        return 0.0, 0.0, 0.0, 0.0

st.divider()
with st.expander("📖 Como funciona este Monitor? (Clique para ver detalhes)"):
    st.markdown(f"""
    ### ☕ Lógica de Cálculo
    Este site realiza uma simulação do impacto do mercado financeiro global no preço físico do café no Espírito Santo:
    
    1.  **Preço Base:** Buscamos diariamente as cotações oficiais de **Bebida Dura** e **Bebida Rio** diretamente do site do **CCCV** (Centro do Comércio de Café de Vitória).
    2.  **Variação Combinada:** O sistema monitora em tempo real a oscilação da **Bolsa de Nova York (KC=F)** e do **Dólar (USD/BRL)**. 
    3.  **Alvo Estimado:** Aplicamos a soma dessas variações sobre o preço base. Se a Bolsa sobe 1% e o Dólar sobe 1%, o alvo estimado subirá aproximadamente 2% sobre o valor de fechamento do CCCV.

    ---
    ⚠️ **Aviso de Versão Beta**
    Este site ainda está em fase de testes (**Beta**). Os valores apresentados são estimativas matemáticas para auxiliar na tomada de decisão e não devem ser considerados como garantia de preço de compra ou venda. As cooperativas locais podem aplicar diferenciais (basis) específicos.
    
    **Criado por: Marcos Gomes**
    """)

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

    # --- BEBIDA DURA ---
    mudanca_dura = base_dura * var_total
    with col_d:
        st.subheader("☕ Bebida DURA")
        # CORREÇÃO: Passamos o número puro para o delta e forçamos delta_color="normal"
        st.metric(
            label="Alvo Estimado", 
            value=f"R$ {base_dura + mudanca_dura:.2f}", 
            delta=float(round(mudanca_dura, 2)),
            delta_color="normal"
        )

    # --- BEBIDA RIO ---
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
