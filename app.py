import streamlit as st
import pandas as pd
import plotly.express as px
import io
from datetime import datetime, timedelta
from fpdf import FPDF

# 1. Configuração da página com identidade visual em tons de verde
st.set_page_config(page_title="Matriz GUT + RACI + Cronograma", layout="wide")

st.title("📊 Gestão Estratégica: GUT + RACI + Cronograma")
st.markdown("Priorize problemas, atribua responsabilidades e gira os prazos de execução num único lugar.")

# 2. Inicialização do estado da sessão (Dados iniciais de simulação)
if "dados_estrategicos" not in st.session_state:
    hoje = datetime.today()
    st.session_state.dados_estrategicos = pd.DataFrame([
        {
            "Problema": "Atraso no inventário anual de bens móveis e verificação de plaquetas patrimoniais", 
            "G": 4, "U": 4, "T": 3,
            "Aprovador (A)": "Diretor de Administração", "Responsável (R)": "Equipa de Património",
            "Consultados (C)": "Contabilidade", "Informados (I)": "Auditoria Interna",
            "Início": hoje.strftime("%Y-%m-%d"), "Conclusão": (hoje + timedelta(days=15)).strftime("%Y-%m-%d")
        },
        {
            "Problema": "Inconsistência crônica em relatórios de depreciação contábil do encerramento do exercício", 
            "G": 5, "U": 3, "T": 4,
            "Aprovador (A)": "Chefe de Finanças", "Responsável (R)": "Contabilista Líder",
            "Consultados (C)": "TI (Suporte)", "Informados (I)": "Diretoria Executiva",
            "Início": hoje.strftime("%Y-%m-%d"), "Conclusão": (hoje + timedelta(days=7)).strftime("%Y-%m-%d")
        }
    ])

# 3. Formulário de Cadastro de novas ações com prazos e RACI
with st.form("novo_problema_form", clear_on_submit=True):
    st.subheader("🆕 Cadastrar Nova Ação Estratégica")
    
    col1, col2, col3, col4 = st.columns([4, 2, 2, 2])
    with col1:
        descricao = st.text_input("Descrição do Problema/Gargalo:")
    with col2:
        g = st.selectbox("Gravidade (G):", [1, 2, 3, 4, 5], help="1: Sem gravidade | 5: Extremamente grave")
    with col3:
        u = st.selectbox("Urgência (U):", [1, 2, 3, 4, 5], help="1: Pode esperar | 5: Ação imediata")
    with col4:
        t = st.selectbox("Tendência (T):", [1, 2, 3, 4, 5], help="1: Vai diminuir | 5: Vai piorar rapidamente")
    
    # Linha para a Matriz RACI
    st.markdown("**Atribuição de Papéis (Matriz RACI):**")
    raci_col1, raci_col2, raci_col3, raci_col4 = st.columns(4)
    with raci_col1:
        aprovador = st.text_input("Aprovador (A):", placeholder="Ex: Diretor da Área")
    with raci_col2:
        responsavel = st.text_input("Responsável (R):", placeholder="Ex: João / Equipa X")
    with raci_col3:
        consultados = st.text
        
