import streamlit as st
import base64
import sqlite3
from datetime import date

# Configuração da página
st.set_page_config(page_title="Gerador Pimaco com Banco de Dados", layout="wide")

# -------------------------------------------------------------------------
# CONFIGURAÇÃO DO BANCO DE DADOS (SQLite)
# -------------------------------------------------------------------------
def conectar_banco():
    conn = sqlite3.connect("produtos.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE,
            nome_cor TEXT,
            quantidade TEXT,
            base TEXT,
            variacao TEXT,
            valor TEXT
        )
    """)
    conn.commit()
    return conn, cursor

conn, cursor = conectar_banco()

# -------------------------------------------------------------------------
# INTERFACE PRINCIPAL
# -------------------------------------------------------------------------
st.title("🏷️ Gerador Pimaco A4354 com Banco de Dados")

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
            
        botao_salvar = st.form_submit_button("💾 Salvar no Banco de Dados")
        
        if botao_salvar:
            if not cad_codigo:
                st.error("O campo 'Código do Produto' é obrigatório!")
            else:
                try:
                    cursor.execute("""
                        INSERT INTO produtos (codigo, nome_cor, quantidade, base, variacao, valor)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (cad_codigo, cad_cor, cad_qtd, cad_base, cad_lote, cad_valor))
                    conn.commit()
                    st.success("Produto " + str(cad_codigo) + " cadastrado com sucesso!")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("Este código de produto já existe no banco de dados!")

    # Visualizar produtos cadastrados
    st.divider()
    st.subheader("📋 Produtos Salvos")
    cursor.execute("SELECT codigo, nome_cor, base, quantidade, variacao, valor FROM produtos")
    lista_produtos = cursor.fetchall()
    
    if lista_produtos:
        st.dataframe(
            lista_produtos, 
            column_config={
                "0": "Código", "1": "Cor", "2": "Base", "3": "Quantidade", "4": "Lote", "5": "Valor"
            },
            use_container_width=True
        )
    else:
        st.info("Nenhum produto cadastrado ainda.")

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

    # SISTEMA DE BUSCA: Carrega dados do banco
    st.subheader("🔍 Buscar Produto Salvo")
    cursor.execute("SELECT codigo FROM produtos")
    todos_codigos = [row[0] for row in cursor.fetchall()]
    
    # Valores padrão iniciais caso o banco esteja vazio
    dados_carregados = {"codigo": "", "cor": "Azul Turquesa", "base": "Acrílica", "qtd": "12 Unids", "lote": "Lote B-1", "valor": "29,90"}
    
    selecao_busca = st.selectbox("Escolha um produto cadastrado para preencher os campos abaixo automaticamente:", ["-- Selecione um Código --"] + todos_codigos)
    
    if selecao_busca != "-- Selecione um Código --":
        cursor.execute("SELECT codigo, nome_cor, base, quantidade, variacao, valor FROM produtos WHERE codigo = ?", (selecao_busca,))
        prod = cursor.fetchone()
        if prod:
            dados_carregados = {"codigo": prod[0], "cor": prod[1], "base": prod[2], "qtd": prod[3], "lote": prod[4], "valor": prod[5]}

    st.divider()

    col_dados, col_config = st.columns(2)

    with col_config:
        st.subheader("📏 Configuração do Papel")
        modelo_selecionado = st.selectbox("Selecione o Modelo da Folha:", list(MODELOS_PIMACO.keys()))
        medidas = MODELOS_PIMACO[modelo_selecionado]
        
        largura, altura, colunas, linhas = medidas["largura"], medidas["altura"], medidas["colunas"], medidas["linhas"]
        capacidade_maxima = colunas * linhas
        
        st.success("🎯 **Gabarito:** " + str(largura) + "mm x " + str(altura) + "mm (Máx: " + str(capacidade_maxima) + " etiquetas)")

        st.divider()
        st.subheader("🖨️ Opções de Posição")
        modo_impressao = st.radio("Formato:", ["Folha Completa / Múltiplas", "Apenas 1 Etiqueta Avançada"])
        
        posicao_inicial = st.number_input("Começar a imprimir a partir de qual etiqueta? (1 a " + str(capacidade_maxima) + ")", min_value=1, max_value=capacidade_maxima, value=1)
        
        if modo_impressao == "Folha Completa / Múltiplas":
            vagas_restantes = capacidade_maxima - (posicao_inicial - 1)
            qtd_imprimir = st.number_input("Quantas etiquetas quer gerar?", min_value=1, max_value=vagas_restantes, value=vagas_restantes)
        else:
            qtd_imprimir = 1

        st.divider()
        st.subheader("🔤 Ajuste do Texto")
        tamanho_fonte = st.slider("Tamanho da letra das informações (pixels):", min_value=7, max_value=14, value=9, step=1)

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
        logo_html = '<img src="data:image/png;base64,' + b64_logo + '" class="logo">'
    else:
        logo_html = '<div class="logo-placeholder">SUA MARCA</div>'

    # Funções de geração de blocos HTML estruturados linha por linha
    def gerar_html_etiqueta():
        html = '<div class="etiqueta" style="width: ' + str(largura) + 'mm; height: ' + str(altura) + 'mm;">'
        html += '    <div class="bloco-superior">'
        html += '        ' + logo_html
        html += '        <div class="cod-box">' + str(codigo) + '</div>'
        html += '    </div>'
        html += '    <div class="bloco-central">'
        html += '        <div class="linha">'
        html += '            <span class="item"><span class="lbl">Cor:</span><span class="edit" contenteditable="true">' + str(nome_cor) + '</span></span>'
        html += '            <span class="item"><span class="lbl">Base:</span><span class="edit" contenteditable="true">' + str(base) + '</span></span>'
        html += '        </div>'
        html += '        <div class="linha">'
        html += '            <span class="item"><span class="lbl">Qtd:</span><span class="edit" contenteditable="true">' + str(quantidade) + '</span></span>'
        html += '            <span class="item"><span class="lbl">Lote:</span><span class="edit" contenteditable="true">' + str(variacao) + '</span></span>'
        html += '            <span class="item"><span class="lbl">Data:</span><span class="edit" contenteditable="true">' + data_val.strftime('%d/%m/%Y') + '</span></span>'
        html += '        </div>'
        html += '    </div>'
        html += '    <div class="bloco-preco">RS ' + str(valor) + '</div>'
        html += '</div>'
        return html

    def gerar_etiqueta_vazia():
        return '<div class="etiqueta-vazia" style="width: ' + str(largura) + 'mm; height: ' + str(altura) + 'mm;"></div>'

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

    # Construção de todo o CSS e botão de forma 100% linear livre de aspas triplas
    css_dinamico = "<style>"
    css_dinamico += "  body *, header, footer, .stApp { visibility: hidden !important; }"
