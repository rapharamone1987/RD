import streamlit as st
import pandas as pd
import plotly.express as px
import io
from datetime import datetime, timedelta
from fpdf import FPDF

# 1. Configuração da página com identidade visual em tons de verde
st.set_page_config(page_title="Matriz GUT + RACI + Cronograma", layout="wide")

st.title("📊 Gestão Estratégica: GUT + RACI + Cronograma")
st.markdown("Priorize tarefas, atribua responsabilidades e gira os prazos de execução num único lugar.")

# 2. Inicialização do estado da sessão (Dados iniciais de simulação)
if "dados_estrategicos" not in st.session_state:
    hoje = datetime.today()
    st.session_state.dados_estrategicos = pd.DataFrame([
        {
            "Tarefa": "Realizar o inventário anual de bens móveis e verificação de plaquetas patrimoniais", 
            "G": 4, "U": 4, "T": 3,
            "Aprovador (A)": "Diretor de Administração", "Responsável (R)": "Equipa de Património",
            "Consultados (C)": "Contabilidade", "Informados (I)": "Auditoria Interna",
            "Início": hoje.strftime("%Y-%m-%d"), "Conclusão": (hoje + timedelta(days=15)).strftime("%Y-%m-%d")
        },
        {
            "Tarefa": "Corrigir inconsistências em relatórios de depreciação contábil do encerramento do exercício", 
            "G": 5, "U": 3, "T": 4,
            "Aprovador (A)": "Chefe de Finanças", "Responsável (R)": "Contabilista Líder",
            "Consultados (C)": "TI (Suporte)", "Informados (I)": "Diretoria Executiva",
            "Início": hoje.strftime("%Y-%m-%d"), "Conclusão": (hoje + timedelta(days=7)).strftime("%Y-%m-%d")
        }
    ])

# 3. Formulário de Cadastro
with st.form("novo_problema_form", clear_on_submit=True):
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
        responsavel = st.text_input("Responsável (R):", placeholder="Ex: João / Equipa X")
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

# 5. Processamento Geral dos Dados
df = st.session_state.dados_estrategicos.copy()
df["Score"] = df["G"] * df["U"] * df["T"]
df = df.sort_values(by="Score", ascending=False).reset_index(drop=True)

df_para_grafico = df.copy()

df["Início"] = pd.to_datetime(df["Início"]).dt.strftime("%d/%m/%Y")
df["Conclusão"] = pd.to_datetime(df["Conclusão"]).dt.strftime("%d/%m/%Y")

ordem_colunas = ["Tarefa", "G", "U", "T", "Score", "Início", "Conclusão", "Aprovador (A)", "Responsável (R)", "Consultados (C)", "Informados (I)"]
df = df[ordem_colunas]

# 6. Gráfico Interativo para a Tela
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

# 7. Classe Customizada para o PDF com Elementos Institucionais (Molduras, Faixas e Rodapés)
class PDFExecutivo(FPDF):
    def header(self):
        # 1. Desenha a Borda Externa de Margem em toda a folha (A4 Paisagem tem 297x210mm)
        self.set_draw_color(180, 180, 180)
        self.set_line_width(0.3)
        self.rect(10, 10, 277, 190, "D")
        
        # 2. Desenha a Faixa Verde do Cabeçalho
        self.set_fill_color(27, 94, 32) # Verde Escuro
        self.rect(12, 12, 273, 14, "F")
        
        # Texto dentro da Faixa Verde
        self.set_xy(15, 14)
        self.set_font("Arial", "B", 14)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, "PLANO DE ACCAO E GOVERNACAO ESTRATEGICA", align="L")
        
    def footer(self):
        # 3. Desenha a Faixa Verde Fina do Rodapé
        self.set_fill_color(44, 160, 90) # Verde Médio
        self.rect(12, 191, 273, 1.5, "F")
        
        # Texto e Paginação do Rodapé
        self.set_y(193)
        self.set_x(15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(120, 120, 120)
        data_hoje = datetime.today().strftime('%d/%m/%Y')
        self.cell(100, 5, f"Documento Institucional - Emitido em: {data_hoje}", align="L")
        
        self.set_x(240)
        self.cell(40, 5, f"Pagina {self.page_no()}", align="R")

# 8. Renderização do Painel Visual do Streamlit
layout_col1, layout_col2 = st.columns([6, 4])

with layout_col1:
    st.subheader("📋 Painel de Governação e Prazos")
    
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

    # Botões de Exportação
    if not df.empty:
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            buffer_xlsx = io.BytesIO()
            with pd.ExcelWriter(buffer_xlsx, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Plano de Trabalho')
                worksheet = writer.sheets['Plano de Trabalho']
                for col in worksheet.columns:
                    max_len = max(len(str(cell.value or '')) for cell in col)
                    worksheet.column_dimensions[col[0].column_letter].width = max(max_len + 3, 12)

            st.download_button(
                label="📄 Exportar Planilha Excel (.xlsx)", data=buffer_xlsx.getvalue(),
                file_name="plano_trabalho_gut_raci.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            
        with col_btn2:
            # Utiliza a nossa classe customizada com Cabeçalhos e Rodapés Premium
            pdf = PDFExecutivo(orientation="L", unit="mm", format="A4")
            pdf.add_page()
            
            # Recuo técnico inicial para não colar os dados na faixa do topo
            pdf.set_y(32)
            pdf.set_x(12)
            
            # Subtítulo da Página 1
            pdf.set_font("Arial", "B", 11)
            pdf.set_text_color(50, 50, 50)
            pdf.cell(0, 8, "I. Matriz de Priorizacao (GUT) e Distribuicao de Papeis (RACI)", ln=True)
            pdf.ln(2)
            
            # Cabeçalho interno da tabela
            pdf.set_fill_color(38, 50, 56) # Azul Escuro Industrial para diferenciar do topo máster
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Arial", "B", 8.5)
            
            w_tarefa, w_g, w_u, w_t, w_score, w_data, w_raci = 83, 7, 7, 7, 12, 22, 28
            pdf.set_x(12) # Alinhamento rígido com a margem interna das faixas
            pdf.cell(w_tarefa, 8, "Tarefa Estrategica", border=1, fill=True)
            pdf.cell(w_g, 8, "G", border=1, fill=True, align="C")
            pdf.cell(w_u, 8, "U", border=1, fill=True, align="C")
            pdf.cell(w_t, 8, "T", border=1, fill=True, align="C")
            pdf.cell(w_score, 8, "Score", border=1, fill=True, align="C")
            pdf.cell(w_data, 8, "Inicio", border=1, fill=True, align="C")
            pdf.cell(w_data, 8, "Conclusao", border=1, fill=True, align="C")
            pdf.cell(w_raci, 8, "Aprovador (A)", border=1, fill=True)
            pdf.cell(w_raci, 8, "Responsavel (R)", border=1, fill=True)
            pdf.cell(w_raci, 8, "Consultado (C)", border=1, fill=True)
            pdf.cell(w_raci, 8, "Informado (I)", border=1, fill=True, ln=True)
            
            # Linhas da Tabela
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", "", 8)
            
            for idx, row in df.iterrows():
                bg = idx % 2 == 1
                pdf.set_fill_color(244, 250, 245) if bg else pdf.set_fill_color(255, 255, 255)
                
                pdf.set_x(12)
                x_inicio = pdf.get_x()
                y_inicio = pdf.get_y()
                
                pdf.multi_cell(w_tarefa, 5, row['Tarefa'], border=1, fill=bg)
                y_fim = pdf.get_y()
                altura_linha = max(6, y_fim - y_inicio) 
                
                pdf.set_xy(x_inicio + w_tarefa, y_inicio)
                pdf.cell(w_g, altura_linha, str(row['G']), border=1, fill=bg, align="C")
                pdf.cell(w_u, altura_linha, str(row['U']), border=1, fill=bg, align="C")
                pdf.cell(w_t, altura_linha, str(row['T']), border=1, fill=bg, align="C")
                
                if int(row['Score']) >= 60:
                    pdf.set_text_color(198, 40, 40)
                    pdf.set_font("Arial", "B", 8)
                
                pdf.cell(w_score, altura_linha, str(row['Score']), border=1, fill=bg, align="C")
                pdf.set_text_color(0, 0, 0)
                pdf.set_font("Arial", "", 8)
                
                pdf.cell(w_data, altura_linha, row['Início'], border=1, fill=bg, align="C")
                pdf.cell(w_data, altura_linha, row['Conclusão'], border=1, fill=bg, align="C")
                pdf.cell(w_raci, altura_linha, str(row['Aprovador (A)']), border=1, fill=bg)
                pdf.cell(w_raci, altura_linha, str(row['Responsável (R)']), border=1, fill=bg)
                pdf.cell(w_raci, altura_linha, str(row['Consultados (C)']), border=1, fill=bg)
                pdf.cell(w_raci, altura_linha, str(row['Informados (I)']), border=1, fill=bg, ln=True)
            
            # --- CRONOGRAMA EM CARDS NA PÁGINA 2 ---
            pdf.add_page()
            pdf.set_y(32)
            pdf.set_x(12)
            
            pdf.set_font("Arial", "B", 11)
            pdf.set_text_color(50, 50, 50)
            pdf.cell(0, 8, "II. Mapa de Prazos de Execucao (Visao Linear)", ln=True)
            pdf.ln(3)
            
            for idx, row in df.iterrows():
                pdf.set_x(15)
                y_card_inicio = pdf.get_y()
                
                pdf.set_y(y_card_inicio + 2)
                pdf.set_x(18)
                
                pdf.set_font("Arial", "B", 9)
                pdf.set_text_color(0, 0, 0)
                pdf.multi_cell(255, 5, f"{idx+1}. {row['Tarefa']}", border=0)
                
                pdf.ln(2) 
                
                score_val = int(row['Score'])
                if score_val >= 60:
                    pdf.set_fill_color(27, 94, 32)   
                elif score_val >= 30:
                    pdf.set_fill_color(44, 160, 90)  
                else:
                    pdf.set_fill_color(161, 219, 178) 
                
                largura_barra = max(15, min(100, score_val * 1.3))
                y_barra = pdf.get_y()
                pdf.rect(18, y_barra + 1, largura_barra, 4, "F")
                
                pdf.set_font("Arial", "", 8.5)
                pdf.set_text_color(80, 80, 80)
                pdf.set_x(23 + largura_barra)
                pdf.cell(0, 6, f"Prazo: {row['Início']} a {row['Conclusão']} | Responsável: {row['Responsável (R)']}", ln=True)
                
                y_card_fim = pdf.get_y() + 2
                
                # Borda sutil de cada card
                pdf.set_draw_color(200, 200, 200) 
                pdf.set_line_width(0.2)
                altura_card = y_card_fim - y_card_inicio
                pdf.rect(15, y_card_inicio, 267, altura_card, "D")
                
                pdf.set_y(y_card_fim + 4) 
            
            pdf.set_draw_color(0, 0, 0) 
            
            pdf_output = pdf.output()
            st.download_button(
                label="📕 Exportar Relatório PDF (.pdf)", data=bytes(pdf_output),
                file_name="relatorio_cronograma_tarefas.pdf", mime="application/pdf",
                use_container_width=True
            )

with layout_col2:
    st.subheader("📊 Volume de Criticidade")
    if not df.empty:
        fig_bar = px.bar(
            df, x="Score", y="Tarefa", orientation="h", text="Score", color="Score",
            color_continuous_scale=["#a1dbb2", "#2ca05a", "#1b5e20"]
        )
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False, margin=dict(l=10, r=10, t=10, b=10), height=250)
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Nenhuma tarefa registada.")

# 8. Cronograma Interativo no Ecrã (Gantt)
st.markdown("---")
st.subheader("📅 Cronograma Interativo de Execução (Linha do Tempo)")
if not df.empty:
    st.plotly_chart(fig_gantt, use_container_width=True)
else:
    st.info("Adicione tarefas para visualizar o mapa do cronograma.")
            
