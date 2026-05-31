import streamlit as st
import pandas as pd
import plotly.express as px
import io
from datetime import datetime, timedelta

# Configuração da página com tons de verde
st.set_page_config(page_title="Matriz GUT + RACI + Cronograma", layout="wide")

st.title("📊 Gestão Estratégica: GUT + RACI + Cronograma")
st.markdown("Priorize problemas, atribua responsabilidades e gira os prazos de execução num único lugar.")

# 1. Inicialização do estado da sessão (GUT + RACI + Datas)
if "dados_estrategicos" not in st.session_state:
    hoje = datetime.today()
    st.session_state.dados_estrategicos = pd.DataFrame([
        {
            "Problema": "Atraso no inventário anual de bens móveis", 
            "G": 4, "U": 4, "T": 3,
            "Aprovador (A)": "Diretor de Administração", "Responsável (R)": "Equipa de Património",
            "Consultados (C)": "Contabilidade", "Informados (I)": "Auditoria Interna",
            "Início": hoje.strftime("%Y-%m-%d"), "Conclusão": (hoje + timedelta(days=15)).strftime("%Y-%m-%d")
        },
        {
            "Problema": "Inconsistência em relatórios de depreciação contábil", 
            "G": 5, "U": 3, "T": 4,
            "Aprovador (A)": "Chefe de Finanças", "Responsável (R)": "Contabilista Líder",
            "Consultados (C)": "TI (Suporte)", "Informados (I)": "Diretoria Executiva",
            "Início": hoje.strftime("%Y-%m-%d"), "Conclusão": (hoje + timedelta(days=7)).strftime("%Y-%m-%d")
        }
    ])

# 2. Cadastro de novos problemas com prazos
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
        consultados = st.text_input("Consultados (C):", placeholder="Ex: Setor de TI")
    with raci_col4:
        informados = st.text_input("Informados (I):", placeholder="Ex: Secretário")
        
    # Linha para Prazos
    st.markdown("**Cronograma de Execução:**")
    data_col1, data_col2 = st.columns(2)
    with data_col1:
        data_inicio = st.date_input("Data de Início da Ação:", datetime.today())
    with data_col2:
        data_fim = st.date_input("Prazo para Conclusão:", datetime.today() + timedelta(days=10))
        
    submit = st.form_submit_button("Adicionar à Matriz de Trabalho")

# Processa a inserção dos novos dados
if submit and descricao:
    if data_inicio > data_fim:
        st.error("Erro: A data de início não pode ser posterior ao prazo de conclusão!")
    else:
        novo_dado = pd.DataFrame([{
            "Problema": descricao, "G": g, "U": u, "T": t,
            "Aprovador (A)": aprovador, "Responsável (R)": responsavel,
            "Consultados (C)": consultados, "Informados (I)": informados,
            "Início": data_inicio.strftime("%Y-%m-%d"),
            "Conclusão": data_fim.strftime("%Y-%m-%d")
        }])
        st.session_state.dados_estrategicos = pd.concat([st.session_state.dados_estrategicos, novo_dado], ignore_index=True)
        st.rerun()

# 3. Processamento dos Dados
df = st.session_state.dados_estrategicos.copy()
df["Score"] = df["G"] * df["U"] * df["T"]
df = df.sort_values(by="Score", ascending=False).reset_index(drop=True)

# Organização das colunas
ordem_colunas = [
    "Problema", "G", "U", "T", "Score", 
    "Início", "Conclusão", 
    "Aprovador (A)", "Responsável (R)", "Consultados (C)", "Informados (I)"
]
df = df[ordem_colunas]

# 4. Exibição dos Resultados
layout_col1, layout_col2 = st.columns([6, 4])

with layout_col1:
    st.subheader("📋 Painel de Governação e Prazos")
    
    df_editor = df.copy()
    df_editor.insert(0, "Excluir", False)
    
    dados_editados = st.data_editor(
        df_editor,
        use_container_width=True,
        hide_index=True,
        disabled=ordem_colunas,
        column_config={"Excluir": st.column_config.CheckboxColumn(required=True)}
    )
    
    if dados_editados["Excluir"].any():
        indices_para_manter = dados_editados[~dados_editados["Excluir"]].index
        problemas_manter = dados_editados.loc[indices_para_manter, "Problema"].tolist()
        st.session_state.dados_estrategicos = st.session_state.dados_estrategicos[st.session_state.dados_estrategicos["Problema"].isin(problemas_manter)]
        st.rerun()

    # Botão de Exportação para Excel (Incluindo as Datas)
    if not df.empty:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Plano de Trabalho')
            worksheet = writer.sheets['Plano de Trabalho']
            for col in worksheet.columns:
                max_len = max(len(str(cell.value or '')) for cell in col)
                worksheet.column_dimensions[col[0].column_letter].width = max(max_len + 3, 12)

        st.download_button(
            label="📄 Exportar Cronograma Completo (.xlsx)",
            data=buffer.getvalue(),
            file_name="plano_trabalho_gut_raci.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

with layout_col2:
    st.subheader("📊 Criticidade por Volume")
    if not df.empty:
        fig_bar = px.bar(
            df, x="Score", y="Problema", orientation="h", text="Score", color="Score",
            color_continuous_scale=["#a1dbb2", "#2ca05a", "#1b5e20"]
        )
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False, margin=dict(l=10, r=10, t=10, b=10), height=250)
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Nenhum dado registado.")

# =========================================================
# NOVA SECÇÃO: VISUALIZAÇÃO DE CALENDÁRIO / LINHA DO TEMPO
# =========================================================
st.markdown("---")
st.subheader("📅 Cronograma Interativo de Execução (Linha do Tempo)")

if not df.empty:
    # Garantir que as colunas estão no formato de data para o gráfico reconhecer
    df_timeline = df.copy()
    df_timeline["Início"] = pd.to_datetime(df_timeline["Início"])
    df_timeline["Conclusão"] = pd.to_datetime(df_timeline["Conclusão"])
    
    # Criar o gráfico de Gantt usando Plotly Timeline
    fig_gantt = px.timeline(
        df_timeline,
        x_start="Início",
        x_end="Conclusão",
        y="Problema",
        color="Score",
        color_continuous_scale=["#a1dbb2", "#2ca05a", "#1b5e20"],
        title="Prazos de Entrega Ordenados por Impacto Estratégico",
        hover_data={"Aprovador (A)": True, "Responsável (R)": True, "Score": True}
    )
    
    # Ajustar o layout para que fique intuitivo e profissional
    fig_gantt.update_layout(
        yaxis={'categoryorder': 'total ascending'}, # Problemas mais críticos no topo
        xaxis_title="Linha do Tempo",
        yaxis_title="",
        coloraxis_colorbar=dict(title="Score GUT"),
        margin=dict(l=20, r=20, t=40, b=20),
        height=350
    )
    
    # Renderizar o calendário/cronograma em largura total
    st.plotly_chart(fig_gantt, use_container_width=True)
else:
    st.info("Adicione problemas para visualizar o mapa do cronograma.")
    
