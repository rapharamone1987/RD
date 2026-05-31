import streamlit as st
import pandas as pd
import plotly.express as px
import io

# Configuração da página com tons de verde
st.set_page_config(page_title="Matriz GUT + RACI", layout="wide")

st.title("📊 Gestão Estratégica: Matriz GUT + RACI")
st.markdown("Priorize os problemas da sua gestão e defina os papéis e responsabilidades para cada um.")

# 1. Inicialização do estado da sessão para armazenar os dados (GUT + RACI)
if "dados_estrategicos" not in st.session_state:
    st.session_state.dados_estrategicos = pd.DataFrame([
        {
            "Problema": "Atraso no inventário anual de bens móveis", 
            "G": 4, "U": 4, "T": 3,
            "Aprovador (A)": "Diretor de Administração", "Responsável (R)": "Equipa de Património",
            "Consultados (C)": "Contabilidade", "Informados (I)": "Auditoria Interna"
        },
        {
            "Problema": "Inconsistência em relatórios de depreciação contábil", 
            "G": 5, "U": 3, "T": 4,
            "Aprovador (A)": "Chefe de Finanças", "Responsável (R)": "Contabilista Líder",
            "Consultados (C)": "TI (Suporte)", "Informados (I)": "Diretoria Executiva"
        }
    ])

# 2. Cadastro de novos problemas com GUT e RACI
with st.form("novo_problema_form", clear_on_submit=True):
    st.subheader("🆕 Cadastrar Problema e Atribuir Responsabilidades")
    
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
        aprovador = st.text_input("Aprovador (A) - Dono da entrega:", placeholder="Ex: Diretor da Área")
    with raci_col2:
        responsavel = st.text_input("Responsável (R) - Quem executa:", placeholder="Ex: João / Equipa X")
    with raci_col3:
        consultados = st.text_input("Consultados (C) - Quem ajuda:", placeholder="Ex: Setor de TI, Jurídico")
    with raci_col4:
        informados = st.text_input("Informados (I) - Quem acompanha:", placeholder="Ex: Secretário, RH")
        
    submit = st.form_submit_button("Adicionar à Matriz Estratégica")

# Adiciona o novo problema e recarrega a página para atualizar os gráficos
if submit and descricao:
    novo_dado = pd.DataFrame([{
        "Problema": descricao, "G": g, "U": u, "T": t,
        "Aprovador (A)": aprovador, "Responsável (R)": responsavel,
        "Consultados (C)": consultados, "Informados (I)": informados
    }])
    st.session_state.dados_estrategicos = pd.concat([st.session_state.dados_estrategicos, novo_dado], ignore_index=True)
    st.rerun()

# 3. Processamento dos Dados
df = st.session_state.dados_estrategicos.copy()
df["Score"] = df["G"] * df["U"] * df["T"]
# Ordenação por Score crítico
df = df.sort_values(by="Score", ascending=False).reset_index(drop=True)

# Reorganizar as colunas para a tabela ficar intuitiva (Score primeiro que a RACI)
ordem_colunas = ["Problema", "G", "U", "T", "Score", "Aprovador (A)", "Responsável (R)", "Consultados (C)", "Informados (I)"]
df = df[ordem_colunas]

# 4. Exibição dos Resultados
layout_col1, layout_col2 = st.columns([6, 4])

with layout_col1:
    st.subheader("📋 Painel de Priorização e Governação (GUT + RACI)")
    
    # Editor para exclusão visual
    df_editor = df.copy()
    df_editor.insert(0, "Excluir", False)
    
    dados_editados = st.data_editor(
        df_editor,
        use_container_width=True,
        hide_index=True,
        disabled=["Problema", "G", "U", "T", "Score", "Aprovador (A)", "Responsável (R)", "Consultados (C)", "Informados (I)"],
        column_config={"Excluir": st.column_config.CheckboxColumn(required=True)}
    )
    
    if dados_editados["Excluir"].any():
        indices_para_manter = dados_editados[~dados_editados["Excluir"]].index
        problemas_manter = dados_editados.loc[indices_para_manter, "Problema"].tolist()
        st.session_state.dados_estrategicos = st.session_state.dados_estrategicos[st.session_state.dados_estrategicos["Problema"].isin(problemas_manter)]
        st.rerun()

    # Botão de Exportação para Excel atualizado com RACI
    if not df.empty:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='GUT + RACI')
            worksheet = writer.sheets['GUT + RACI']
            for col in worksheet.columns:
                max_len = max(len(str(cell.value or '')) for cell in col)
                col_letter = col[0].column_letter
                worksheet.column_dimensions[col_letter].width = max(max_len + 3, 12)

        st.download_button(
            label="📄 Exportar Planilha de Governação (.xlsx)",
            data=buffer.getvalue(),
            file_name="matriz_gut_raci.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

with layout_col2:
    st.subheader("📈 Nível de Criticidade")
    if not df.empty:
        fig = px.bar(
            df, 
            x="Score", 
            y="Problema", 
            orientation="h",
            text="Score",
            color="Score",
            color_continuous_scale=["#a1dbb2", "#2ca05a", "#1b5e20"]
        )
        fig.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nenhum problema registado.")
    
