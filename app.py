import streamlit as st
import base64
from datetime import datetime, date
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import a4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, Image as RLImage, String

# Configuração da página
st.set_page_config(page_title="Gerador Pimaco PDF", layout="wide")

# -------------------------------------------------------------------------
# BANCO DE DADOS EM MEMÓRIA
# -------------------------------------------------------------------------
if "banco_etiquetas" not in st.session_state:
    st.session_state["banco_etiquetas"] = pd.DataFrame(
        columns=["Data_Hora", "Codigo", "Cor", "Base", "Quantidade", "Lote", "Valor"]
    )

# -------------------------------------------------------------------------
# INTERFACE PRINCIPAL
# -------------------------------------------------------------------------
st.title("🏷️ Gerador Pimaco A4354 - Versão PDF")

aba_etiquetas, aba_historico = st.tabs(["🖨️ Gerar Etiquetas", "📜 Histórico de Etiquetas Impressas"])

# ABA 2: HISTÓRICO
with aba_historico:
    st.subheader("📋 Relatório de Etiquetas Já Emitidas")
    if not st.session_state["banco_etiquetas"].empty:
        st.dataframe(st.session_state["banco_etiquetas"], use_container_width=True, hide_index=True)
        csv = st.session_state["banco_etiquetas"].to_csv(index=False).encode('utf-8-sig')
        st.download_button(label="📥 Baixar Histórico em Excel (CSV)", data=csv, file_name="historico_etiquetas.csv", mime="text/csv")
    else:
        st.info("Nenhuma etiqueta foi gravada no histórico desta sessão ainda.")

# ABA 1: GERADOR
with aba_etiquetas:
    # Medidas oficiais da folha Pimaco A4354 convertidas para pontos (medida do PDF)
    # 1 mm = 2.83465 pontos
    LARGURA_ETIQ = 99.0 * 2.83465
    ALTURA_ETIQ = 25.4 * 2.83465
    MARGEM_SUP = 21.2 * 2.83465
    MARGEM_ESQ = 6.0 * 2.83465
    GAP_COL = 10.0 * 2.83465
    COLUNAS = 2
    LINHAS = 11

    col_dados, col_config = st.columns(2)

    with col_config:
        st.subheader("⚙️ Opções de Posição")
        posicao_inicial = st.number_input("Começar a imprimir a partir de qual etiqueta? (1 a 22)", min_value=1, max_value=22, value=1)
        qtd_imprimir = st.number_input("Quantas etiquetas quer gerar?", min_value=1, max_value=23-posicao_inicial, value=23-posicao_inicial)
        tamanho_fonte = st.slider("Tamanho da letra:", min_value=7, max_value=12, value=9, step=1)

    with col_dados:
        st.subheader("📝 Informações da Etiqueta")
        c1, c2, c3 = st.columns(3)
        with c1:
            codigo = st.text_input("Código", value="REF-1020")
            nome_cor = st.text_input("Nome da Cor", value="Azul Turquesa")
        with c2:
            base = st.text_input("Base", value="Acrílica")
            quantidade = st.text_input("Quantidade", value="12 Unids")
        with c3:
            variacao = st.text_input("Variação/Lote", value="Lote B-1")
            valor = st.text_input("Valor RS", value="29,90")
            
        data_val = st.date_input("Data de Validade", date.today())
        logo_file = st.file_uploader("Upload da Logomarca (Opcional)", type=["png", "jpg", "jpeg"])

    # -------------------------------------------------------------------------
    # FUNÇÃO QUE CONSTRÓI A ETQUETA DENTRO DO PDF
    # -------------------------------------------------------------------------
    def desenhar_etiqueta(vazia=False):
        # Cria um bloco de desenho do tamanho exato da etiqueta Pimaco
        d = Drawing(LARGURA_ETIQ, ALTURA_ETIQ)
        if vazia:
            return d
        
        # Se tiver logo, processa a imagem para o PDF
        if logo_file is not None:
            logo_file.seek(0)
            img_data = logo_file.read()
            b64_img = base64.b64encode(img_data).decode()
            d.add(RLImage(5, ALTURA_ETIQ - 20, 70, 15, f"data:image/png;base64,{b64_img}"))
        else:
            d.add(String(5, ALTURA_ETIQ - 15, "[SUA MARCA]", fontSize=7, fontName="Helvetica-Bold", fillColor=colors.lightgrey))
        
        # Injeta os textos nas posições horizontais e verticais corretas
        d.add(String(LARGURA_ETIQ - 50, ALTURA_ETIQ - 15, str(codigo), fontSize=tamanho_fonte, fontName="Helvetica-Bold"))
        d.add(String(5, ALTURA_ETIQ - 32, "Cor: " + str(nome_cor), fontSize=tamanho_fonte, fontName="Helvetica"))
        d.add(String(130, ALTURA_ETIQ - 32, "Base: " + str(base), fontSize=tamanho_fonte, fontName="Helvetica"))
        d.add(String(5, ALTURA_ETIQ - 48, "Qtd: " + str(quantidade), fontSize=tamanho_fonte, fontName="Helvetica"))
        d.add(String(65, ALTURA_ETIQ - 48, "Lote: " + str(variacao), fontSize=tamanho_fonte, fontName="Helvetica"))
        d.add(String(130, ALTURA_ETIQ - 48, "Val: " + data_val.strftime('%d/%m/%Y'), fontSize=tamanho_fonte, fontName="Helvetica"))
        d.add(String(LARGURA_ETIQ - 55, 5, "RS " + str(valor), fontSize=tamanho_fonte + 2, fontName="Helvetica-Bold", fillColor=colors.HexColor("#1b5e20")))
        return d

    # -------------------------------------------------------------------------
    # CONSTRUÇÃO DO ARQUIVO PDF COMPLETO
    # -------------------------------------------------------------------------
    buffer = BytesIO()
    # Cria o documento A4 com margens zero para controlarmos via tabela interna
    doc = SimpleDocTemplate(buffer, pagesize=a4, leftMargin=0, rightMargin=0, topMargin=0, bottomMargin=0)
    
    # Organiza a lista de etiquetas pulando as vazias iniciais
    etiquetas_lista = []
    for _ in range(posicao_inicial - 1):
        etiquetas_lista.append(desenhar_etiqueta(vazia=True))
    for _ in range(qtd_imprimir):
        etiquetas_lista.append(desenhar_etiqueta(vazia=False))
    while len(etiquetas_lista) < 22:
        etiquetas_lista.append(desenhar_etiqueta(vazia=True))

    # Divide a lista em 11 linhas com 2 colunas cada
    dados_grade = []
    for i in range(0, 22, 2):
        dados_grade.append([etiquetas_lista[i], etiquetas_lista[i+1]])

    # Monta a estrutura de tabela aplicando os recuos milimétricos da Pimaco
    tabela = Table(dados_grade, colWidths=[LARGURA_ETIQ, LARGURA_ETIQ])
    tabela.setStyle(TableStyle([
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        # Separa as duas colunas aplicando o vão central de 10mm
        ('RIGHTPADDING', (0,0), (0,-1), GAP_COL), 
    ]))

    # Define a distância exata do topo e da lateral esquerda da folha A4
    grade_com_margem = Table([[tabela]], colWidths=[a4[0]])
    grade_com_margem.setStyle(TableStyle([
        ('LEFTPADDING', (0,0), (-1,-1), MARGEM_ESQ),
        ('TOPPADDING', (0,0), (-1,-1), MARGEM_SUP),
    ]))

    doc.build([grade_com_margem])
    pdf_data = buffer.getvalue()

    # -------------------------------------------------------------------------
    # BOTÃO ÚNICO DE SALVAMENTO E RELATÓRIO
    # -------------------------------------------------------------------------
    st.write("### 🖨️ Concluir Operação")
    
    # Toda vez que o usuário clicar para baixar o PDF, essa função roda nos bastidores salvando a linha na tabela
    def registrar_e_imprimir():
        novo_registro = {
            "Data_Hora": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "Codigo": codigo,
            "Cor": nome_cor,
            "Base": base,
            "Quantidade": quantidade,
            "Lote": variacao,
            "Valor": valor
        }
        st.session_state["banco_etiquetas"] = pd.concat(
            [st.session_state["banco_etiquetas"], pd.DataFrame([novo_registro])], 
            ignore_index=True
        )

    st.download_button(
        label="💾 Salvar no Relatório e Baixar Folha em PDF",
        data=pdf_data,
        file_name="folha_etiquetas_pimaco.pdf",
        mime="application/pdf",
        on_click=registrar_e_imprimir,
        help="Clique aqui para salvar os dados na planilha e gerar o arquivo de impressão perfeito."
    )
