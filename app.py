import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página com a identidade visual que você curte (tons de verde)
st.set_page_config(page_title="Matriz GUT Interativa", layout="wide")

st.title("📊 Matriz GUT - Priorização Estratégica")
st.markdown("Insira os problemas da sua gestão e defina os pesos para **Gravidade, Urgência e Tendência**.")

# 1. Cadastro de novos problemas
with st.form("novo_problema_form", clear_on_submit=True):
    col1, col2, col3, col4 = st.columns([4, 2, 2, 2])
    with col1:
        descricao = st.text_input("Descrição do Problema/Gargalo:")
    with col2:
        g = st.selectbox("Gravidade (G):", [1, 2, 3, 4, 5], help="1: Sem gravidade | 5: Extremamente grave")
    with col3:
        u = st.selectbox("Urgência (U):", [1, 2, 3, 4, 5], help="1: Pode esperar | 5: Ação imediata")
    with col4:
        t = st.selectbox("Tendência (T):", [1, 2, 3, 4, 5], help="1: Vai diminuir | 5: Vai piorar rapidamente")
    
    submit = st.form_submit_button("Adicionar Problema")

# 2. Inicialização do estado da sessão para armazenar os dados
if "dados_gut" not in st.session_state:
    # Dados de simulação baseados em cenários comuns de administração e patrimônio
    st.session_state.dados_gut = pd.DataFrame([
        {"Problema": "Atraso no inventário anual de bens móveis", "G": 4, "U": 4, "T": 3},
        {"Problema": "Inconsistência em relatórios de depreciação contábil", "G": 5, "U": 3, "T": 4},
        {"Problema": "Fluxo manual de requisição de materiais no SharePoint", "G": 3, "U": 5, "T": 3},
        {"Problema": "Falta de treinamento de novos servidores em conformidade", "G": 3, "U": 2, "T": 4}
    ])

# Adiciona o novo problema digitado pelo usuário
if submit and descricao:
    novo_dado = pd.DataFrame([{"Problema": descricao, "G": g, "U": u, "T": t}])
    st.session_state.dados_gut = pd.concat([st.session_state.dados_gut, novo_dado], ignore_index=True)

# 3. Processamento dos Dados
df = st.session_state.dados_gut.copy()
# Cálculo do Score GUT: G x U x T
df["Score"] = df["G"] * df["U"] * df["T"]
# Ordenação do maior para o menor (prioridade máxima no topo)
df = df.sort_values(by="Score", ascending=False).reset_index(drop=True)

# 4. Exibição dos Resultados
layout_col1, layout_col2 = st.columns([5, 5])

with layout_col1:
    st.subheader("📋 Tabela de Priorização (Ordenada)")
    # Renderiza a tabela de forma elegante
    st.dataframe(df, use_container_width=True)

with layout_col2:
    st.subheader("📈 Gráfico de Criticidade")
    # Gráfico de barras horizontal com a paleta de cores verde/alta visibilidade
    fig = px.bar(
        df, 
        x="Score", 
        y="Problema", 
        orientation="h",
        text="Score",
        color="Score",
        color_continuous_scale=["#a1dbb2", "#2ca05a", "#1b5e20"] # Variações de verde
    )
    fig.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
