import streamlit as st
import base64
from datetime import date

# Configuração da página
st.set_page_config(page_title="Gerador Pimaco 22 Etiquetas", layout="wide")

st.title("🏷️ Gerador Profissional - Gabarito Pimaco A4354 (22 Etiquetas)")
st.write("Layout milimétrico configurado para folhas de 22 unidades (25,4mm x 99mm).")

# Banco de dados com o modelo de 22 etiquetas fixado e outras opções
MODELOS_PIMACO = {
    "Pimaco A4354 (25.4mm x 99.0mm - 22 etiq.)": {"largura": 99.0, "altura": 25.4, "colunas": 2, "linhas": 11},
    "Personalizado (Definir Manualmente)": {"largura": 80.0, "altura": 40.0, "colunas": 2, "linhas": 6},
    "Pimaco 6180 (63.5mm x 38.1mm - 21 etiq.)": {"largura": 63.5, "altura": 38.1, "colunas": 3, "linhas": 7},
    "Pimaco 6182 (101.6mm x 33.9mm - 14 etiq.)": {"largura": 101.6, "altura": 33.9, "colunas": 2, "linhas": 7}
}

col_dados, col_config = st.columns([2, 1])

with col_config:
    st.subheader("📏 Modelo do Papel")
    modelo_selecionado = st.selectbox("Selecione o Modelo:", list(MODELOS_PIMACO.keys()))
    medidas = MODELOS_PIMACO[modelo_selecionado]
    
    if modelo_selecionado == "Personalizado (Definir Manualmente)":
        largura = st.number_input("Largura (mm):", value=medidas["largura"])
        altura = st.number_input("Altura (mm):", value=medidas["altura"])
        colunas = st.number_input("Colunas:", value=medidas["colunas"], min_value=1)
        linhas = st.number_input("Linhas:", value=medidas["linhas"], min_value=1)
    else:
        largura = medidas["largura"]
        altura = medidas["altura"]
        colunas = medidas["colunas"]
        linhas = medidas["linhas"]
        st.success(f"🎯 **Gabarito Ativo:** {largura}mm x {altura}mm ({colunas}x{linhas})")

    st.divider()
    st.subheader("🖨️ Modo de Impressão")
    modo_impressao = st.radio("Selecione o destino:", ["Folha Completa (Preencher 22 etiquetas)", "Apenas 1 Etiqueta Única"])
    
    total_etiquetas = (colunas * linhas) if modo_impressao == "Folha Completa (Preencher 22 etiquetas)" else 1

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

# Processamento binário da imagem do Logo
logo_html = ""
if logo_file is not None:
    bytes_data = logo_file.read()
    b64_logo = base64.b64encode(bytes_data).decode()
    logo_html = f'<img src="data:image/png;base64,{b64_logo}" class="logo">'
else:
    logo_html = '<div class="logo-placeholder">SUA MARCA</div>'

# HTML estruturado compacto focado nas proporções horizontais da A4354
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

# CSS Milimétrico para encaixe perfeito nas folhas Pimaco
css_estilo = f"""
<style>
    .grade-etiquetas {{
        display: grid;
        grid-template-columns: repeat({colunas}, {largura}mm);
        gap: 0.5mm 3mm; /* Ajuste milimétrico de margem interna da folha */
        padding: 5mm;
        background: #f0f2f6;
        border-radius: 8px;
        justify-content: start;
    }}
    
    .etiqueta {{
        background: white;
        border: 1px dashed #ccc;
        padding: 1.5mm 2.5mm;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        position: relative;
        overflow: hidden;
    }}
    
    .bloco-superior {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        height: 6mm;
    }}
    
    .logo {{
        max-height: 5.5mm;
        max-width: 35mm;
        object-fit: contain;
    }}
    
    .logo-placeholder {{
        font-size: 7px;
        color: #aaa;
        font-weight: bold;
        border: 1px dotted #ddd;
        padding: 1px 3px;
        line-height: 1;
    }}
    
    .cod-box {{
        font-size: 8px;
        font-weight: bold;
        background: #333;
        color: #fff;
        padding: 0.5px 3px;
        border-radius: 2px;
    }}
    
    .bloco-central {{
        display: flex;
        flex-direction: column;
        justify-content: center;
        height: 11mm;
    }}
    
    .linha {{
        display: flex;
        justify-content: space-between;
        font-size: 8.5px;
        margin-bottom: 0.5mm;
    }}
    
    .item {{
        display: inline-block;
        white-space: nowrap;
    }}
    
    .lbl {{
        font-weight: bold;
        color: #444;
        margin-right: 1px;
    }}
    
    .edit {{
        color: #111;
        padding: 0 1px;
    }}
    
    .edit:hover {{
        background: #fff9c4;
        cursor: pointer;
    }}
    
    .bloco-preco {{
        text-align: right;
        font-size: 10px;
        font-weight: bold;
        color: #1b5e20;
        height: 4mm;
        line-height: 4mm;
        border-top: 1px solid #f5f5f5;
    }}

    /* CSS de Impressora física - Oculta os menus do Streamlit ao imprimir */
    @media print {{
        body * {{
            visibility: hidden;
        }}
        .grade-etiquetas, .grade-etiquetas * {{
            visibility: visible;
        }}
        .grade-etiquetas {{
            position: absolute;
            left: 4mm;  /* Margem esquerda da folha A4 */
            top: 10mm;  /* Margem superior da folha A4 */
            background: white !important;
            grid-template-columns: repeat({colunas}, {largura}mm) !important;
            gap: 0mm 3.5mm !important; /* Espaçamento exato entre as colunas Pimaco */
            padding: 0 !important;
        }}
        .etiqueta {{
            border: 1px transparent solid !important; /* Oculta bordas na impressão real */
            page-break-inside: avoid;
        }}
    }}
</style>
"""

# Renderização final
st.subheader("👁️ Visualização Real da Folha")
html_etiquetas_completo = "".join([gerar_html_etiqueta() for _ in range(total_etiquetas)])
html_final = f"{css_estilo}<div class='grade-etiquetas'>{html_etiquetas_completo}</div>"

st.components.v1.html(html_final, height=600, scrolling=True)

st.info("💡 Pronto para imprimir! Quando clicar no comando de impressão do seu navegador (Ctrl+P), configure a margem como 'Nenhuma' ou 'Padrão' nas propriedades da impressora para não desalinhá-la.")
st.button("🖨️ Atalho de Impressão: Pressione CTRL + P no teclado")
