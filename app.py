import streamlit as st
import base64
from datetime import date

# Configuração da página
st.set_page_config(page_title="Gerador Pimaco Avançado", layout="wide")

st.title("🏷️ Gerador Profissional - Gabarito Pimaco A4354")
st.write("Agora com controle de posição de início para reaproveitamento de folhas!")

# Banco de dados Pimaco
MODELOS_PIMACO = {
    "Pimaco A4354 (25.4mm x 99.0mm - 22 etiq.)": {"largura": 99.0, "altura": 25.4, "colunas": 2, "linhas": 11},
    "Personalizado (Definir Manualmente)": {"largura": 80.0, "altura": 40.0, "colunas": 2, "linhas": 6},
    "Pimaco 6180 (63.5mm x 38.1mm - 21 etiq.)": {"largura": 63.5, "altura": 38.1, "colunas": 3, "linhas": 7}
}

# CORREÇÃO AQUI: Adicionado o número 2 para definir duas colunas na tela
col_dados, col_config = st.columns(2)

with col_config:
    st.subheader("📏 Configuração do Papel")
    modelo_selecionado = st.selectbox("Selecione o Modelo:", list(MODELOS_PIMACO.keys()))
    medidas = MODELOS_PIMACO[modelo_selecionado]
    
    largura = medidas["largura"]
    altura = medidas["altura"]
    colunas = medidas["colunas"]
    linhas = medidas["linhas"]
    capacidade_maxima = colunas * linhas
    
    st.success(f"🎯 **Gabarito:** {largura}mm x {altura}mm (Máx: {capacidade_maxima} etiquetas)")

    st.divider()
    st.subheader("🖨️ Opções de Posição e Impressão")
    
    modo_impressao = st.radio("Formato:", ["Folha Completa / Múltiplas", "Apenas 1 Etiqueta Avançada"])
    
    # Nova função: Seleção de Posição Inicial
    posicao_inicial = st.number_input(
        f"Começar a imprimir a partir de qual etiqueta? (1 a {capacidade_maxima})", 
        min_value=1, 
        max_value=capacidade_maxima, 
        value=1,
        help="Se você já usou as primeiras etiquetas da folha, mude este número para pular os espaços vazios!"
    )
    
    if modo_impressao == "Folha Completa / Múltiplas":
        vagas_restantes = capacidade_maxima - (posicao_inicial - 1)
        qtd_imprimir = st.number_input("Quantas etiquetas quer gerar?", min_value=1, max_value=vagas_restantes, value=vagas_restantes)
    else:
        qtd_imprimir = 1

with col_dados:
    st.subheader("📝 Informações do Produto")
    c1, c2, c3 = st.columns(3)
    with c1:
        nome_cor = st.text_input("Nome da Cor", "Azul Turquesa")
        quantidade = st.text_input("Quantidade", "12 Unids")
        codigo = st.text_input("Código", "REF-2234")
    with c2:
        base = st.text_input("Base", "Acrílica")
        variacao = st.text_input("Variação/Lote", "Lote B-1")
        valor = st.text_input("Valor R$", "29,90")
    with c3:
        data_val = st.date_input("Data", date.today())
        logo_file = st.file_uploader("Upload da Logomarca", type=["png", "jpg", "jpeg"])

# Processamento do Logo
logo_html = ""
if logo_file is not None:
    bytes_data = logo_file.read()
    b64_logo = base64.b64encode(bytes_data).decode()
    logo_html = f'<img src="data:image/png;base64,{b64_logo}" class="logo">'
else:
    logo_html = '<div class="logo-placeholder">SUA MARCA</div>'

# HTML de uma etiqueta preenchida
def gerar_html_etiqueta():
    return f"""
    <div class="etiqueta" style="width: {largura}mm; height: {altura}mm;">
        <div class="bloco-superior">
            {logo_html}
            <div class="cod-box">{codigo}</div>
        </div>
        <div class="bloco-central">
            <div class="linha">
                <span class="item"><span class="lbl">Cor:</span><span class="edit" contenteditable="true">{nome_cor}</span></span>
                <span class="item"><span class="lbl">Base:</span><span class="edit" contenteditable="true">{base}</span></span>
            </div>
            <div class="linha">
                <span class="item"><span class="lbl">Qtd:</span><span class="edit" contenteditable="true">{quantidade}</span></span>
                <span class="item"><span class="lbl">Lote:</span><span class="edit" contenteditable="true">{variacao}</span></span>
                <span class="item"><span class="lbl">Data:</span><span class="edit" contenteditable="true">{data_val.strftime('%d/%m/%Y')}</span></span>
            </div>
        </div>
        <div class="bloco-preco">
            R$ {valor}
        </div>
    </div>
    """

# HTML de uma etiqueta invisível
def gerar_etiqueta_vazia():
    return f'<div class="etiqueta-vazia" style="width: {largura}mm; height: {altura}mm;"></div>'

# Construção da Folha
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

# Estilização CSS e Script de Impressão Direta
css_e_script = f"""
<style>
    .grade-etiquetas {{
        display: grid;
        grid-template-columns: repeat({colunas}, {largura}mm);
        gap: 0.5mm 3mm;
        padding: 5mm;
        background: #f0f2f6;
        border-radius: 8px;
        justify-content: start;
    }}
    
    .etiqueta {{
        background: white;
        border: 1px dashed #ccc;
        padding: 1.5mm 2.5mm;
        font-family: Arial, sans-serif;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        overflow: hidden;
    }}
    
    .etiqueta-vazia {{
        background: #e0e0e0;
        border: 1px dotted #bbb;
        box-sizing: border-box;
        opacity: 0.4;
    }}
    
    .bloco-superior {{ display: flex; justify-content: space-between; align-items: center; height: 6mm; }}
    .logo {{ max-height: 5.5mm; max-width: 35mm; object-fit: contain; }}
    .logo-placeholder {{ font-size: 7px; color: #aaa; font-weight: bold; border: 1px dotted #ddd; padding: 1px 3px; }}
    .cod-box {{ font-size: 8px; font-weight: bold; background: #333; color: #fff; padding: 0.5px 3px; border-radius: 2px; }}
    .bloco-central {{ display: flex; flex-direction: column; justify-content: center; height: 11mm; }}
    .linha {{ display: flex; justify-content: space-between; font-size: 8.5px; margin-bottom: 0.5mm; }}
    .lbl {{ font-weight: bold; color: #444; margin-right: 1px; }}
    .edit:hover {{ background: #fff9c4; cursor: pointer; }}
    .bloco-preco {{ text-align: right; font-size: 10px; font-weight: bold; color: #1b5e20; height: 4mm; border-top: 1px solid #f5f5f5; }}

    .btn-imprimir-real {{
        background-color: #2e7d32;
        color: white;
        border: none;
        padding: 10px 20px;
        font-size: 14px;
        font-weight: bold;
        border-radius: 4px;
        cursor: pointer;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    .btn-imprimir-real:hover {{ background-color: #1b5e20; }}

    @media print {{
        body *, header, footer, .stApp {{
            visibility: hidden !important;
        }}
        .grade-etiquetas, .grade-etiquetas * {{
            visibility: visible !important;
        }}
        .grade-etiquetas {{
            position: absolute !important;
            left: 4mm !important;
            top: 10mm !important;
            background: white !important;
            grid-template-columns: repeat({colunas}, {largura}mm) !important;
            gap: 0mm 3.5mm !important;
            padding: 0 !important;
        }}
        .etiqueta {{ border: 1px transparent solid !important; page-break-inside: avoid; }}
        .etiqueta-vazia {{ border: 1px transparent solid !important; background: transparent !important; opacity: 0 !important; }}
        .btn-imprimir-real {{ display: none !important; }}
    }}
</style>

<button class="btn-imprimir-real" onclick="window.print()">🖨️ Clique Aqui para Imprimir Esta Folha</button>
"""

# Renderização Final do Painel
st.subheader("👁️ Visualização da Folha (Etiquetas cinzas representam espaços que serão pulados)")
html_final = f"{css_e_script}<div class='grade-etiquetas'>{html_etiquetas_completo}</div>"

st.components.v1.html(html_final, height=700, scrolling=True)
