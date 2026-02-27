import streamlit as st
import pandas as pd
import yfinance as yf
import requests

# 1. Configuração da página
st.set_page_config(page_title="Previsão Café ES", page_icon="☕", layout="wide")

# --- INJEÇÃO DE CSS PARA IMAGEM DE FUNDO ---
# Você pode substituir este URL por qualquer link direto de imagem de café.
# Link de exemplo: uma imagem de grãos de café desfocada para não atrapalhar a leitura.
url_imagem_cafe = "https://images.unsplash.com/photo-1501747188-61c00b3d8ba0?q=80&w=1920"

page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] > .main {{
background-image: url("{url_imagem_cafe}");
background-size: cover;
background-position: center;
background-repeat: no-repeat;
background-attachment: fixed;
}}

/* Opcional: Adiciona uma camada escura semi-transparente sobre a imagem 
   para garantir que o texto branco/padrão do Streamlit fique legível */
[data-testid="stAppViewContainer"] > .main::before {{
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.4); /* Preto com 40% de opacidade */
    z-index: -1;
}}

/* Garante que os containers de input/st.metric tenham fundo se necessário para leitura */
[data-testid="stMetricValue"] {{
    background-color: rgba(255, 255, 255, 0.1);
    padding: 5px;
    border-radius: 5px;
}}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)
# ---------------------------------------------


# 2. Funções de captura de dados
def buscar_dados_cccv():
    url = "https://www.cccv.org.br/cotacao/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        tabelas = pd.read_html(response.text)
        df = tabelas[0]
        # Procura linhas que contenham as palavras-chave
        idx_dura = df[df[0].str.contains("dura", case=False, na=False)].index[0]
        idx_rio = df[df[0].str.contains("rio", case=False, na=False)].index[0]
        
        # Pega o valor na coluna 1
        dura_str = df.iloc[idx_dura, 1]
        rio_str = df.iloc[idx_rio, 1]
        
        # Converte para float removendo pontos e trocando vírgula por ponto
        dura = float(str(dura_str).replace('.', '').replace(',', '.'))
        rio = float(str(rio_str).replace('.', '').replace(',', '.'))
        return dura, rio
    except Exception as e:
        # st.error(f"Erro ao buscar CCCV: {e}")
        return 1694.00, 1349.00

def buscar_mercado_completo():
    try:
        # Baixa histórico de 10 dias para garantir que teremos dados suficientes
        cafe_hist = yf.download("KC=F", period="10d", interval="1d", progress=False)['Close']
        dolar_hist = yf.download("USDBRL=X", period="10d", interval="1d", progress=False)['Close']
        
        # Dados atuais para os cards (últimos dois dias úteis)
        cot_ny = float(cafe_hist.iloc[-1].iloc[0]) if hasattr(cafe_hist.iloc[-1], 'iloc') else float(cafe_hist.iloc[-1])
        cot_ny_anterior = float(cafe_hist.iloc[-2].iloc[0]) if hasattr(cafe_hist.iloc[-2], 'iloc') else float(cafe_hist.iloc[-2])
        v_ny = (cot_ny / cot_ny_anterior) - 1
        
        cot_usd = float(dolar_hist.iloc[-1].iloc[0]) if hasattr(dolar_hist.iloc[-1], 'iloc') else float(dolar_hist.iloc[-1])
        cot_usd_anterior = float(dolar_hist.iloc[-2].iloc[0]) if hasattr(dolar_hist.iloc[-2], 'iloc') else float(dolar_hist.iloc[-2])
        v_usd = (cot_usd / cot_usd_anterior) - 1
        
        return cot_ny, v_ny, cot_usd, v_usd, cafe_hist, dolar_hist
    except Exception as e:
        # st.error(f"Erro ao buscar Yahoo Finance: {e}")
        return 0.0, 0.0, 0.0, 0.0, None, None

# --- TÍTULO E EXPLICAÇÃO (NO TOPO) ---
st.title("📊 Monitor de Tendência do Café - ES")

st.markdown("### 📖 Como funciona este Monitor?")
st.write("Este site simula o impacto do mercado financeiro global no preço físico do café no Espírito Santo.")

exp_col1, exp_col2, exp_col3 = st.columns(3)
with exp_col1:
    st.markdown("**1. Preço Base (CCCV)**")
    st.write("Cotações oficiais de fechamento em Vitória.")
with exp_col2:
    st.markdown("**2. Variação Combinada**")
    st.write("Monitoramento em tempo real de NY e do Dólar.")
with exp_col3:
    st.markdown("**3. Alvo Estimado**")
    st.write("Tendência baseada na oscilação internacional.")

st.info("""🕒 **Nota sobre o fechamento:** O CCCV publica os valores exatos entre 16:00 e 17:00. 
Antes disso, o cálculo utiliza o fechamento do dia anterior como base.""")

st.divider()

# --- RESULTADOS ATUAIS ---
# Usando st.spinner para feedback visual enquanto carrega
with st.spinner('Atualizando cotações...'):
    base_dura, base_rio = buscar_dados_cccv()
    ny_p, ny_v, usd_p, usd_v, hist_ny, hist_usd = buscar_mercado_completo()

if ny_p == 0:
    st.warning("Carregando dados da bolsa ou erro na API... Atualize a página em instantes.")
else:
    var_total = ny_v + usd_v
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Bolsa NY (Arábica)", f"{ny_p:.2f} pts", f"{ny_v:.2%}", delta_color="normal")
    c2.metric("Dólar Comercial", f"R$ {usd_p:.2f}", f"{usd_v:.2%}", delta_color="normal")
    c3.metric("Tendência Combinada", f"{(var_total*100):.2f}%")

    st.divider()
    col_d, col_r = st.columns(2)

    mudanca_dura = base_dura * var_total
    with col_d:
        st.subheader("☕ Bebida DURA")
        st.metric(label="Alvo Estimado", value=f"R$ {base_dura + mudanca_dura:.2f}", 
                  delta=float(round(mudanca_dura, 2)), delta_color="normal")

    mudanca_rio = base_rio * var_total
    with col_r:
        st.subheader("☕ Bebida RIO")
        st.metric(label="Alvo Estimado", value=f"R$ {base_rio + mudanca_rio:.2f}", 
                  delta=float(round(mudanca_rio, 2)), delta_color="normal")

    # --- HISTÓRICO DE FECHAMENTO (CORRIGIDO) ---
    st.divider()
    st.subheader("📅 Histórico de Fechamento (Últimos Dias)")
    
    if hist_ny is not None and hist_usd is not None:
        try:
            # Criando o DataFrame alinhando as datas corretamente
            df_final = pd.merge(hist_ny, hist_usd, left_index=True, right_index=True, how='inner')
            df_final.columns = ['Bolsa NY (pts)', 'Dólar (R$)']
            
            # Formata data e organiza
            df_final.index = df_final.index.strftime('%d/%m/%Y')
            
            # Aplica formatação e exibe
            st.dataframe(df_final.sort_index(ascending=False).style.format("{:.2f}"), use_container_width=True)
        except Exception as e:
            st.error(f"Erro ao processar histórico: {e}")

# --- RODAPÉ ---
st.divider()
st.warning("⚠️ **Versão Beta:** Estimativas matemáticas para auxílio na tomada de decisão.")
st.markdown("<br><br><h1 style='text-align: center; color: white;'>Criado por: Marcos Gomes</h1>", unsafe_allow_html=True)
st.caption("Fontes: CCCV e Yahoo Finance.")
