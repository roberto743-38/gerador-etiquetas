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

    # Estilos CSS injetados de forma estável
    css_estilos = "<style>"
    css_estilos += "  .grade-etiquetas { display: grid; grid-template-columns: repeat(" + str(colunas) + ", " + str(largura) + "mm); gap: 1mm 3mm; padding: 5mm; background: #ffffff; border: 2px solid #ddd; border-radius: 8px; justify-content: start; width: fit-content; }"
    css_estilos += "</style>"

    st.subheader("👁️ Visualização da Folha")
    
    # Exibe a pré-visualização das etiquetas na tela de forma limpa e nativa
    html_final_tela = css_estilos + '<div class="grade-etiquetas">' + html_etiquetas_completo + '</div>'
    st.components.v1.html(html_final_tela, height=450, scrolling=True)

    st.divider()
    st.subheader("🖨️ Ações de Impressão")

    # -------------------------------------------------------------------------
    # FUNÇÃO DE SALVAMENTO DISPARADA PELO BOTÃO PYTHON (À Prova de erros)
    # -------------------------------------------------------------------------
    def acao_salvar_historico():
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

    # Botão de salvar no relatório usando lógica nativa Python
    st.button("💾 1º Passo: Gravar Dados no Histórico", on_click=acao_salvar_historico, help="Clique aqui primeiro para salvar as informações no seu relatório.")

    # HTML de Impressão limpo para o arquivo externo
    html_impressao = '<html><head><meta charset="utf-8"><style>'
    html_impressao += 'body { margin: 0; padding: 0; }'
    html_impressao += '.grade { display: grid; grid-template-columns: repeat(' + str(colunas) + ', ' + str(largura) + 'mm) !important; gap: 0mm 3.5mm !important; position: absolute; left: 4mm; top: 10mm; }'
    html_impressao += '.etiqueta { background: white; border: 1px transparent solid !important; page-break-inside: avoid; }'
    html_impressao += '</style></head><body onload="window.print()">'
    html_etiquetas_print = html_etiquetas_completo.replace('background: #f0f2f6; border: 1px dotted #ccc;', 'background: transparent; border: none;')
    html_impressao += '<div class="grade">' + html_etiquetas_print + '</div></body></html>'

    # Botão de download nativo do Streamlit para abrir a folha de impressão
    st.download_button(
