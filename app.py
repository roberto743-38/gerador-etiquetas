import streamlit as st
import base64
from datetime import date

# Configuração da página
st.set_page_config(page_title="Gerador Pimaco Avançado", layout="wide")

# -------------------------------------------------------------------------
# BANCO DE DADOS EM MEMÓRIA (Session State - À prova de falhas na nuvem)
# -------------------------------------------------------------------------
if "banco_produtos" not in st.session_state:
    st.session_state["banco_produtos"] = {}

# -------------------------------------------------------------------------
# INTERFACE PRINCIPAL
# -------------------------------------------------------------------------
st.title("🏷️ Gerador Pimaco A4354 Profissional")

# Criação de Abas para organizar o sistema
aba_etiquetas, aba_cadastro = st.tabs(["🖨️ Gerar Etiquetas", "📦 Cadastrar / Gerenciar Produtos"])

# -------------------------------------------------------------------------
# ABA 2: CADASTRO DE PRODUTOS
# -------------------------------------------------------------------------
with aba_cadastro:
    st.subheader("📝 Cadastrar Novo Produto")
    with st.form("form_cadastro", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            cad_codigo = st.text_input("Código do Produto (Único)*")
            cad_cor = st.text_input("Nome da Cor")
        with c2:
            cad_base = st.text_input("Base")
            cad_qtd = st.text_input("Quantidade Padrão")
        with c3:
            cad_lote = st.text_input("Variação / Lote")
            cad_valor = st.text_input("Valor Padrão RS")
            
        botao_salvar = st.form_submit_button("💾 Salvar Produto")
        
        if botao_salvar:
            if not cad_codigo:
                st.error("O campo 'Código do Produto' é obrigatório!")
            else:
                st.session_state["banco_produtos"][cad_codigo] = {
                    "codigo": cad_codigo,
                    "cor": cad_cor,
                    "base": cad_base,
                    "qtd": cad_qtd,
                    "lote": cad_lote,
                    "valor": cad_valor
                }
                st.success("Produto " + str(cad_codigo) + " salvo com sucesso!")
                st.rerun()

    # Visualizar produtos cadastrados
    st.divider()
    st.subheader("📋 Produtos Salvos Temporariamente")
    if st.session_state["banco_produtos"]:
        dados_tabela = list(st.session_state["banco_produtos"].values())
        st.dataframe(dados_tabela, use_container_width=True)
    else:
        st.info("Nenhum produto cadastrado nesta sessão ainda.")

# -------------------------------------------------------------------------
# ABA 1: GERADOR DE ETIQUETAS
# -------------------------------------------------------------------------
with aba_etiquetas:
    # Banco de dados de folhas Pimaco
    MODELOS_PIMACO = {
        "Pimaco A4354 (25.4mm x 99.0mm - 22 etiq.)": {"largura": 99.0, "altura": 25.4, "colunas": 2, "linhas": 11},
        "Personalizado (Definir Manualmente)": {"largura": 80.0, "altura": 40.0, "colunas": 2, "linhas": 6},
        "Pimaco 6180 (63.5mm x 38.1mm - 21 etiq.)": {"largura": 63.5, "altura": 38.1, "colunas": 3, "linhas": 7}
    }

    # SISTEMA DE BUSCA: Carrega dados salvos
    st.subheader("🔍 Buscar Produto Salvo")
    todos_codigos = list(st.session_state["banco_produtos"].keys())
    
    dados_carregados = {"codigo": "", "cor": "Azul Turquesa", "base": "Acrílica", "qtd": "12 Unids", "lote": "Lote B-1", "valor": "29,90"}
    
    selecao_busca = st.selectbox("Escolha um produto para preencher automaticamente:", ["-- Selecione um Código --"] + todos_codigos)
    
    if selecao_busca != "-- Selecione um Código --":
        prod = st.session_state["banco_produtos"][selecao_busca]
        dados_carregados = {"codigo": prod["codigo"], "cor": prod["cor"], "base": prod["base"], "qtd": prod["qtd"], "lote": prod["lote"], "valor": prod["valor"]}

    st.divider()

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
        tamanho_fonte = st.slider("Tamanho da letra das informações (pixels):", min_value=7, max_value=14, value=10, step=1)

    with col_dados:
        st.subheader("📝 Informações da Etiqueta")
        c1, c2, c3 = st.columns(3)
        with c1:
            codigo = st.text_input("Código", value=dados_carregados["codigo"])
            nome_cor = st.text_input("Nome da Cor", value=dados_carregados["cor"])
        with c2:
            base = st.text_input("Base", value=dados_carregados["base"])
            quantidade = st.text_input("Quantidade", value=dados_carregados["qtd"])
        with c3:
            variacao = st.text_input("Variação/Lote", value=dados_carregados["lote"])
            valor = st.text_input("Valor RS", value=dados_carregados["valor"])
            
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

    # Funções de geração de blocos HTML estruturados básicos
    def gerar_html_etiqueta():
        html = '<div style="width: ' + str(largura) + 'mm; height: ' + str(altura) + 'mm; background: white; border: 1px dashed #bbb; padding: 1.5mm 2.5mm; font-family: Arial, sans-serif; box-sizing: border-box; display: flex; flex-direction: column; justify-content: space-between; overflow: hidden;">'
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

    # Monta a grade com estilos 100% visíveis na tela
    estilo_grade = 'display: grid; grid-template-columns: repeat(' + str(colunas) + ', ' + str(largura) + 'mm); gap: 1mm 3mm; padding: 5mm; background: #ffffff; border: 2px solid #ddd; border-radius: 8px; justify-content: start; width: fit-content;'
    html_final_tela = '<div style="' + estilo_grade + '">' + html_etiquetas_completo + '</div>'

    st.subheader("👁️ Visualização da Folha")
    
    # Exibição segura de código HTML puro na tela
    st.components.v1.html(html_final_tela, height=450, scrolling=True)

    # -------------------------------------------------------------------------
    # SISTEMA DE IMPRESSÃO VIA DOWNLOAD DE PAGINA EXTERNA
