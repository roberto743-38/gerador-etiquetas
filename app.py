import streamlit as st
import base64
from datetime import datetime, date
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Gerador Pimaco Profissional", layout="wide")

# -------------------------------------------------------------------------
# BANCO DE DADOS EM MEMÓRIA
# -------------------------------------------------------------------------
if "banco_etiquetas" not in st.session_state:
    st.session_state["banco_etiquetas"] = pd.DataFrame(
        columns=["Data_Hora", "Codigo", "Cor", "Base", "Quantidade", "Lote", "Valor"]
    )

# Captura de dados vindo do clique do botão HTML
query_params = st.query_params
if "salvar_codigo" in query_params:
    cod = query_params["salvar_codigo"]
    novo_registro = {
        "Data_Hora": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "Codigo": cod,
        "Cor": query_params.get("salvar_cor", ""),
        "Base": query_params.get("salvar_base", ""),
        "Quantidade": query_params.get("salvar_qtd", ""),
        "Lote": query_params.get("salvar_lote", ""),
        "Valor": query_params.get("salvar_valor", "")
    }
    st.session_state["banco_etiquetas"] = pd.concat(
        [st.session_state["banco_etiquetas"], pd.DataFrame([novo_registro])], 
        ignore_index=True
    )
    st.query_params.clear()
    st.rerun()

# -------------------------------------------------------------------------
# INTERFACE PRINCIPAL
# -------------------------------------------------------------------------
st.title("🏷️ Gerador Pimaco A4354 Profissional")

aba_etiquetas, aba_historico = st.tabs(["🖨️ Gerar e Imprimir", "📜 Histórico de Etiquetas Impressas"])

# -------------------------------------------------------------------------
# ABA 2: HISTÓRICO DE IMPRESSÕES
# -------------------------------------------------------------------------
with aba_historico:
    st.subheader("📋 Relatório de Etiquetas Já Emitidas")
    
    if not st.session_state["banco_etiquetas"].empty:
        st.dataframe(st.session_state["banco_etiquetas"], use_container_width=True, hide_index=True)
        csv = st.session_state["banco_etiquetas"].to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 Baixar Histórico em Excel (CSV)",
            data=csv,
            file_name="historico_etiquetas.csv",
            mime="text/csv"
        )
    else:
        st.info("Nenhuma etiqueta foi gravada no histórico desta sessão ainda.")

# -------------------------------------------------------------------------
# ABA 1: GERADOR DE ETIQUETAS
# -------------------------------------------------------------------------
with aba_etiquetas:
    MODELOS_PIMACO = {
        "Pimaco A4354 (25.4mm x 99.0mm - 22 etiq.)": {"largura": 99.0, "altura": 25.4, "colunas": 2, "linhas": 11},
        "Personalizado (Definir Manualmente)": {"largura": 80.0, "altura": 40.0, "colunas": 2, "linhas": 6}
    }

    col_dados, col_config = st.columns(2)

    with col_config:
        st.subheader("📏 Configuração do Papel")
        modelo_selecionado = st.selectbox("Selecione o Modelo da Folha:", list(MODELOS_PIMACO.keys()))
        medidas = MODELOS_PIMACO[modelo_selecionado]
        
        largura = medidas["largura"]
        altura = medidas["altura"]
        colunas = medidas["colunas"]
        linhas = medidas["linhas"]
        capacidade_maxima = colunas * linhas
        
        st.success("Gabarito Ativo: " + str(largura) + "mm x " + str(altura) + "mm")

        st.divider()
        st.subheader("🖨️ Opções de Posição")
        modo_impressao = st.radio("Formato:", ["Folha Completa / Múltiplas", "Apenas 1 Etiqueta Avançada"])
        posicao_inicial = st.number_input("Começar a imprimir a partir de qual etiqueta?", min_value=1, max_value=capacidade_maxima, value=1)
        
        if modo_impressao == "Folha Completa / Múltiplas":
            vagas_restantes = capacidade_maxima - (posicao_inicial - 1)
            qtd_imprimir = st.number_input("Quantas etiquetas quer gerar?", min_value=1, max_value=vagas_restantes, value=vagas_restantes)
        else:
            qtd_imprimir = 1

        st.divider()
        st.subheader("🔤 Ajuste do Texto")
        tamanho_fonte = st.slider("Tamanho da letra (pixels):", min_value=7, max_value=14, value=10, step=1)

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
        logo_file = st.file_uploader("Upload da Logomarca", type=["png", "jpg", "jpeg"])

    # Processamento do Logo
    logo_html = ""
    if logo_file is not None:
        bytes_data = logo_file.read()
        b64_logo = base64.b64encode(bytes_data).decode()
        logo_html = '<img src="data:image/png;base64,' + b64_logo + '" style="max-height: 5.5mm; max-width: 35mm; object-fit: contain;">'
    else:
        logo_html = '<div style="font-size: 7px; color: #aaa; font-weight: bold; border: 1px dotted #ddd; padding: 1px 3px;">SUA MARCA</div>'

    # Geração das etiquetas em HTML
    def gerar_html_etiqueta():
        html = '<div class="etiqueta" style="width: ' + str(largura) + 'mm; height: ' + str(altura) + 'mm; background: white; border: 1px dashed #bbb; padding: 1.5mm 2.5mm; font-family: Arial, sans-serif; box-sizing: border-box; display: flex; flex-direction: column; justify-content: space-between; overflow: hidden;">'
        html += '    <div style="display: flex; justify-content: space-between; align-items: center; height: 6mm;">'
        html += '        ' + logo_html
        html += '        <div style="font-size: ' + str(tamanho_fonte - 1) + 'px; font-weight: bold; background: #333; color: #fff; padding: 0.5px 3px; border-radius: 2px;">' + str(codigo) + '</div>'
        html += '    </div>'
        html += '    <div style="display: flex; flex-direction: column; justify-content: center; height: 11mm;">'
        html += '        <div style="display: flex; justify-content: space-between; font-size: ' + str(tamanho_fonte) + 'px; margin-bottom: 0.5mm; color: black;">'
        html += '            <span><b>Cor:</b> ' + str(nome_cor) + '</span>'
        html += '            <span><b>Base:</b> ' + str(base) + '</span>'
        html += '        </div>'
        html += '        <div style="display: flex; justify-content: space-between; font-size: ' + str(tamanho_fonte) + 'px; margin-bottom: 0.5mm; color: black;">'
        html += '            <span><b>Qtd:</b> ' + str(quantidade) + '</span>'
        html += '            <span><b>Lote:</b> ' + str(variacao) + '</span>'
        html += '            <span><b>Data:</b> ' + data_val.strftime('%d/%m/%Y') + '</span>'
        html += '        </div>'
        html += '    </div>'
        html += '    <div style="text-align: right; font-size: ' + str(tamanho_fonte + 2) + 'px; font-weight: bold; color: #1b5e20; height: 4mm; border-top: 1px solid #f5f5f5;">RS ' + str(valor) + '</div>'
        html += '</div>'
        return html

    def gerar_etiqueta_vazia():
        return '<div style="width: ' + str(largura) + 'mm; height: ' + str(altura) + 'mm; background: #f0f2f6; border: 1px dotted #ccc; box-sizing: border-box;"></div>'

    lista_html_final = []
    for _ in range(posicao_inicial - 1):
        lista_html_final.append(gerar_etiqueta_vazia())
    for _ in range(qtd_imprimir):
        lista_html_final.append(gerar_html_etiqueta())
        
    total_gerado = len(lista_html_final)
    if total_gerado < capacidade_maxima:
        for _ in range(capacidade_maxima - total_gerado):
            lista_html_final.append(gerar_etiqueta_vazia())

    html_etiquetas_completo = "".join(lista_html_final)

    # Estilos CSS injetados de forma 100% visível na tela
    css_estilos = "<style>"
    css_estilos += "  .grade-etiquetas { display: grid; grid-template-columns: repeat(" + str(colunas) + ", " + str(largura) + "mm); gap: 1mm 3mm; padding: 5mm; background: #ffffff; border: 2px solid #ddd; border-radius: 8px; justify-content: start; width: fit-content; }"
    css_estilos += "  .btn-print-sistema { background-color: #2e7d32; color: white; border: none; padding: 12px 24px; font-size: 15px; font-weight: bold; border-radius: 4px; cursor: pointer; margin-top: 15px; display: inline-block; text-decoration: none; }"
    css_estilos += "  .btn-print-sistema:hover { background-color: #1b5e20; }"
    css_estilos += "  @media print {"
    css_estilos += "    body *, header, footer, .stTabs, .stElementContainer, .stMarkdown, .stAlert, div[data-testid='stHeader'], div[class*='stSidebar'], .btn-print-sistema { visibility: hidden !important; height: 0 !important; margin: 0 !important; padding: 0 !important; }"
    css_estilos += "    .grade-etiquetas, .grade-etiquetas * { visibility: visible !important; }"
    css_estilos += "    .grade-etiquetas { position: absolute !important; left: 4mm !important; top: 10mm !important; background: white !important; border: none !important; grid-template-columns: repeat(" + str(colunas) + ", " + str(largura) + "mm) !important; gap: 0mm 3.5mm !important; padding: 0 !important; }"
    css_estilos += "    .etiqueta { border: 1px transparent solid !important; page-break-inside: avoid; }"
    css_estilos += "    .etiqueta-vazia { border: 1px transparent solid !important; background: transparent !important; }"
    css_estilos += "  }"
    css_estilos += "</style>"

    st.subheader("👁️ Visualização da Folha")
    
    # Renderização via markdown (Injeção segura sem usar iframes bloqueados)
