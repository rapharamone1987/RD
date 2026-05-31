import streamlit as st
import pandas as pd
import plotly.express as px
import io
from datetime import datetime, timedelta
from fpdf import FPDF
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.formatting.rule import CellIsRule

# 1. Configuração da página com identidade visual em tons de verde
st.set_page_config(page_title="Matriz GUT + RACI + Cronograma", layout="wide")

st.title("📊 Gestão Estratégica: GUT + RACI + Cronograma")
st.markdown("Priorize tarefas, atribua responsabilidades e gerencie os prazos de execução em um único lugar.")

# 2. Inicialização do estado da sessão (Dados iniciais no padrão PT-BR)
if "dados_estrategicos" not in st.session_state:
    hoje = datetime.today()
    st.session_state.dados_estrategicos = pd.DataFrame([
        {
            "Tarefa": "Realizar o inventário anual de bens móveis e verificação de plaquetas patrimoniais", 
            "G": 4, "U": 4, "T": 3,
            "Aprovador (A)": "Diretor de Administração", "Responsável (R)": "Equipe de Patrimônio",
            "Consultados (C)": "Contabilidade", "Informados (I)": "Auditoria Interna",
            "Início": hoje.strftime("%Y-%m-%d"), "Conclusão": (hoje + timedelta(days=15)).strftime("%Y-%m-%d")
        },
        {
            "Tarefa": "Corrigir inconsistências em relatórios de depreciação contábil do encerramento do exercício", 
            "G": 5, "U": 3, "T": 4,
            "Aprovador (A)": "Chefe de Finanças", "Responsável (R)": "Contador Líder",
            "Consultados (C)": "TI (Suporte)", "Informados (I)": "Diretoria Executiva",
            "Início": hoje.strftime("%Y-%m-%d"), "Conclusão": (hoje + timedelta(days=7)).strftime("%Y-%m-%d")
        }
    ])

# 3. Formulário de Cadastro (PT-BR)
with st.form("nova_tarefa_form", clear_on_submit=True):
    st.subheader("🆕 Cadastrar Nova Tarefa Estratégica")
    
    col1, col2, col3, col4 = st.columns([4, 2, 2, 2])
    with col1:
        descricao = st.text_input("Descrição da Tarefa:")
    with col2:
        g = st.selectbox("Gravidade (G):", [1, 2, 3, 4, 5], help="1: Sem gravidade | 5: Extremamente grave")
    with col3:
        u = st.selectbox("Urgência (U):", [1, 2, 3, 4, 5], help="1: Pode esperar | 5: Ação imediata")
    with col4:
        t = st.selectbox("Tendência (T):", [1, 2, 3, 4, 5], help="1: Estável | 5: Vai piorar rapidamente se não agir")
    
    st.markdown("**Atribuição de Papéis (Matriz RACI):**")
    raci_col1, raci_col2, raci_col3, raci_col4 = st.columns(4)
    with raci_col1:
        aprovador = st.text_input("Aprovador (A):", placeholder="Ex: Diretor da Área")
    with raci_col2:
        responsavel = st.text_input("Responsável (R):", placeholder="Ex: João / Equipe X")
    with raci_col3:
        consultados = st.text_input("Consultados (C):", placeholder="Ex: Setor de TI")
    with raci_col4:
        informados = st.text_input("Informados (I):", placeholder="Ex: Secretário")
        
    st.markdown("**Cronograma de Execução:**")
    data_col1, data_col2 = st.columns(2)
    with data_col1:
        data_inicio = st.date_input("Data de Início da Tarefa:", datetime.today(), format="DD/MM/YYYY")
    with data_col2:
        data_fim = st.date_input("Prazo para Conclusão:", datetime.today() + timedelta(days=10), format="DD/MM/YYYY")
        
    submit = st.form_submit_button("Adicionar à Matriz de Trabalho")

# 4. Processamento da submissão
if submit and descricao:
    if data_inicio > data_fim:
        st.error("Erro: A data de início não pode ser posterior ao prazo de conclusão!")
    else:
        novo_dado = pd.DataFrame([{
            "Tarefa": descricao, "G": g, "U": u, "T": t,
            "Aprovador (A)": aprovador, "Responsável (R)": responsavel,
            "Consultados (C)": consultados, "Informados (I)": informados,
            "Início": data_inicio.strftime("%Y-%m-%d"),
            "Conclusão": data_fim.strftime("%Y-%m-%d")
        }])
        st.session_state.dados_estrategicos = pd.concat([st.session_state.dados_estrategicos, novo_dado], ignore_index=True)
        st.rerun()

# 5. Processamento e Ordenação dos Dados
df = st.session_state.dados_estrategicos.copy()
df["Score"] = df["G"] * df["U"] * df["T"]
df = df.sort_values(by="Score", ascending=False).reset_index(drop=True)

df_para_grafico = df.copy()

df["Início"] = pd.to_datetime(df["Início"]).dt.strftime("%d/%m/%Y")
df["Conclusão"] = pd.to_datetime(df["Conclusão"]).dt.strftime("%d/%m/%Y")

ordem_colunas = ["Tarefa", "G", "U", "T", "Score", "Início", "Conclusão", "Aprovador (A)", "Responsável (R)", "Consultados (C)", "Informados (I)"]
df = df[ordem_colunas]

# 6. Gráfico Interativo para a Tela (Corrigido para evitar erros de bloco vazio)
fig_gantt = None
if not df.empty:
    df_timeline = df_para_grafico.copy()
    df_timeline["Início"] = pd.to_datetime(df_timeline["Início"])
    df_timeline["Conclusão"] = pd.to_datetime(df_timeline["Conclusão"])
    
    fig_gantt = px.timeline(
        df_timeline, x_start="Início", x_end="Conclusão", y="Tarefa", color="Score",
        color_continuous_scale=["#a1dbb2", "#2ca05a", "#1b5e20"]
    )
    fig_gantt.update_xaxes(tickformat="%d/%m")
    fig_gantt.update_layout(
        yaxis={'categoryorder': 'total ascending'}, 
        xaxis_title="Linha do Tempo (Dia/Mês)", yaxis_title="",
        coloraxis_colorbar=dict(title="Score GUT"), margin=dict(l=20, r=20, t=40, b=20), height=350
    )

# 7. Classe do PDF Customizada (Bordas Máster, Cabeçalhos e Rodapés em PT-BR)
class PDFExecutivo(FPDF):
    def header(self):
        self.set_draw_color(180, 180, 180)
        self.set_line_width(0.3)
        self.rect(10, 10, 277, 190, "D")
        
        self.set_fill_color(27, 94, 32) 
        self.rect(12, 12, 273, 14, "F")
        
        self.set_xy(15, 14)
        self.set_font("Arial", "B", 14)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, "PLANO DE AÇÃO E GOVERNANÇA ESTRATÉGICA", align="L")
        
    def footer(self):
        self.set_fill_color(44, 160, 90) 
        self.rect(12, 191, 273, 1.5, "F")
        
        self.set_y(193)
        self.set_x(15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(120, 120, 120)
        data_hoje = datetime.today().strftime('%d/%m/%Y')
        self.cell(100, 5, f"Documento Institucional - Emitido em: {data_hoje}", align="L")
        
        self.set_x(240)
        self.cell(40, 5, f"Página {self.page_no()}", align="R")

# 8. Renderização do Painel Visual do Streamlit
layout_col1, layout_col2 = st.columns([6, 4])

with layout_col1:
    st.subheader("📋 Painel de Governança e Prazos")
    
    df_editor = df.copy()
    df_editor.insert(0, "Excluir", False)
    
    dados_editados = st.data_editor(
        df_editor, use_container_width=True, hide_index=True, disabled=ordem_colunas,
        column_config={"Excluir": st.column_config.CheckboxColumn(required=True)}
    )
    
    if dados_editados["Excluir"].any():
        indices_para_manter = dados_editados[~dados_editados["Excluir"]].index
        tarefas_manter = dados_editados.loc[indices_para_manter, "Tarefa"].tolist()
        st.session_state.dados_estrategicos = st.session_state.dados_estrategicos[st.session_state.dados_estrategicos["Tarefa"].isin(tarefas_manter)]
        st.rerun()

    if not df.empty:
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            buffer_xlsx = io.BytesIO()
            with pd.ExcelWriter(buffer_xlsx, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Plano de Trabalho')
                worksheet = writer.sheets['Plano de Trabalho']
                
                fonte_cabecalho = Font(name='Calibri', size=11, bold=True, color='FFFFFF')
                preenchimento_cabecalho = PatternFill(start_color='1B5E20', end_color='1B5E20', fill_type='solid') 
                preenchimento_zebra = PatternFill(start_color='F4FAF5', end_color='F4FAF5', fill_type='solid')     
                
                alinhamento_centro = Alignment(horizontal='center', vertical='center', wrap_text=True)
                alinhamento_esquerda = Alignment(horizontal='left', vertical='center', wrap_text=True)
                
                borda_fina_estilo = Side(border_style="thin", color="D3D3D3")
                borda_grade = Border(left=borda_fina_estilo, right=borda_fina_estilo, top=borda_fina_estilo, bottom=borda_fina
                
