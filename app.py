import streamlit as st
import pandas as pd
import os
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

# -------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA (OTIMIZADA PARA CELULAR)
# -------------------------------------------------------------
st.set_page_config(
    page_title="Mix Distribuidora - Amostras",
    page_icon="📦",
    layout="centered",
    initial_sidebar_state="collapsed")

# Adiciona meta tags para funcionamento como App nativo em celulares
st.markdown("""
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="mobile-web-app-capable" content="yes">
""", unsafe_allow_html=True)

# Estilização CSS Responsiva para Telas Menores
st.markdown("""
<style>
    /* Ajustes Gerais para Celulares */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        padding-left: 0.8rem;
        padding-right: 0.8rem;
        max-width: 100% !important;
    }
    
    /* Cabeçalho Compacto */
    .header-mobile {
        background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 100%);
        padding: 16px;
        border-radius: 12px;
        color: white;
        margin-bottom: 16px;
        text-align: center;
    }
    .header-mobile h2 {
        font-size: 20px !important;
        font-weight: 700;
        margin: 0;
        color: #FFFFFF !important;
    }
    .header-mobile p {
        font-size: 12px;
        opacity: 0.85;
        margin-top: 4px;
        margin-bottom: 0;
    }

    /* Botões Otimizados para o Polegar */
    div.stButton > button {
        width: 100% !important;
        height: 48px !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
    }
    
    /* Rótulos dos Campos */
    .stSelectbox label, .stTextInput label, .stNumberInput label {
        font-size: 14px !important;
        font-weight: 600 !important;
        color: #1E293B !important;
    }
</style>
""", unsafe_allow_html=True)

from pathlib import Path

# Obtém o caminho absoluto do diretório onde o app.py está executando
BASE_DIR = Path(__file__).parent
PATH_PRODUTOS = BASE_DIR / "amostras gratis.csv"
PATH_CLIENTES = BASE_DIR / "clientes.csv"

@st.cache_data
def carregar_clientes():
    if PATH_CLIENTES.exists():
        clientes = []
        try:
            with open(PATH_CLIENTES, 'r', encoding='latin1', errors='ignore') as f:
                for line in f:
                    partes = [p.strip() for p in line.split(';') if p.strip()]
                    if partes and partes[0].isdigit():
                        codigo = partes[0]
                        nome = partes[1] if len(partes) > 1 else ""
                        if nome and "Vendedor:" not in line:
                            clientes.append({"Codigo": codigo, "Nome": nome})
            return pd.DataFrame(clientes)
        except Exception as e:
            st.error(f"Erro ao ler clientes.csv: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

@st.cache_data
def carregar_produtos():
    if PATH_PRODUTOS.exists():
        produtos = []
        try:
            with open(PATH_PRODUTOS, 'r', encoding='latin1', errors='ignore') as f:
                for line in f:
                    partes = [p.strip() for p in line.split(';') if p.strip()]
                    if partes and partes[0].isdigit():
                        codigo = partes[0]
                        descricao = partes[1] if len(partes) > 1 else ""
                        produtos.append({"Codigo": codigo, "Descricao": f"{codigo} - {descricao}"})
            return pd.DataFrame(produtos)
        except Exception as e:
            st.error(f"Erro ao ler amostras gratis.csv: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

# -------------------------------------------------------------
# GERADOR DE PDF (REPORTLAB)
# -------------------------------------------------------------
def gerar_pdf(codigo_cliente, nome_cliente, itens):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#0F172A"),
        alignment=1,
        spaceAfter=15
    )
    
    label_style = ParagraphStyle(
        'LabelStyle',
        parent=styles['Normal'],
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#334155")
    )

    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=label_style,
        textColor=colors.white,
        fontName="Helvetica-Bold"
    )

    story.append(Paragraph("<b>SOLICITAÇÃO DE AMOSTRAS GRÁTIS</b>", title_style))
    story.append(Spacer(1, 10))

    dados_cliente = [
        [Paragraph(f"<b>CÓDIGO DO CLIENTE:</b> {codigo_cliente}", label_style),
         Paragraph(f"<b>NOME / RAZÃO SOCIAL:</b> {nome_cliente}", label_style)]
    ]
    tabela_cliente = Table(dados_cliente, colWidths=[160, 380])
    tabela_cliente.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(tabela_cliente)
    story.append(Spacer(1, 15))

    tabela_dados = [
        [Paragraph("Item", header_style), 
         Paragraph("Descrição do Produto / Amostra", header_style), 
         Paragraph("Qtd", header_style)]
    ]
    
    for idx, item in enumerate(itens, start=1):
        tabela_dados.append([
            Paragraph(str(idx), label_style),
            Paragraph(item["Descricao"], label_style),
            Paragraph(str(item["Quantidade"]), label_style)
        ])

    tabela_produtos = Table(tabela_dados, colWidths=[40, 420, 80])
    tabela_produtos.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'CENTER'),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    story.append(tabela_produtos)
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# -------------------------------------------------------------
# ESTADO E DADOS
# -------------------------------------------------------------
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

df_clientes = carregar_clientes()
df_produtos = carregar_produtos()

# Topo do App
st.markdown("""
<div class="header-mobile">
    <h2>📦 Pedido de Amostras</h2>
    <p>Mix Distribuidora - Emissão Rápida</p>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# ETAPA 1: DADOS DO CLIENTE
# -------------------------------------------------------------
st.subheader("👤 1. Dados do Cliente")

if not df_clientes.empty:
    lista_codigos = [""] + df_clientes["Codigo"].tolist()
    codigo_sel = st.selectbox("Código do Cliente:", options=lista_codigos)
    
    nome_padrao = ""
    if codigo_sel:
        match = df_clientes[df_clientes["Codigo"] == codigo_sel]
        if not match.empty:
            nome_padrao = match["Nome"].values[0]
            
    nome_cliente = st.text_input("Nome / Razão Social:", value=nome_padrao)
else:
    codigo_sel = st.text_input("Código do Cliente:")
    nome_cliente = st.text_input("Nome / Razão Social:")

st.divider()

# -------------------------------------------------------------
# ETAPA 2: ADICIONAR PRODUTOS
# -------------------------------------------------------------
st.subheader("🛒 2. Selecionar Amostras")

if not df_produtos.empty:
    prod_selecionado = st.selectbox("Produto / Amostra:", options=df_produtos["Descricao"].tolist())
else:
    prod_selecionado = st.text_input("Descrição da Amostra:")

qtd_selecionada = st.number_input("Quantidade (Pacotes/Sacos):", min_value=1, value=1, step=1)

if st.button("➕ Adicionar ao Pedido", type="primary"):
    if prod_selecionado:
        st.session_state.carrinho.append({
            "Descricao": prod_selecionado,
            "Quantidade": int(qtd_selecionada)
        })
        st.toast("Item adicionado!", icon="✅")
        st.rerun()
    else:
        st.warning("Selecione um produto.")

st.divider()

# -------------------------------------------------------------
# ETAPA 3: RESUMO DOS ITENS ADICIONADOS
# -------------------------------------------------------------
st.subheader("📋 3. Itens no Pedido")

if st.session_state.carrinho:
    for idx, item in enumerate(st.session_state.carrinho):
        col_info, col_del = st.columns([4, 1])
        with col_info:
            st.markdown(f"**{item['Descricao']}**")
            st.caption(f"Quantidade: **{item['Quantidade']}**")
        with col_del:
            if st.button("❌", key=f"del_{idx}"):
                st.session_state.carrinho.pop(idx)
                st.rerun()
        st.divider()

    if st.button("🗑️ Limpar Tudo"):
        st.session_state.carrinho = []
        st.rerun()
else:
    st.info("Nenhuma amostra adicionada ainda.")

st.divider()

# -------------------------------------------------------------
# ETAPA 4: GERAR E BAIXAR PDF
# -------------------------------------------------------------
st.subheader("📄 4. Finalizar e Baixar PDF")

if st.button("🚀 Gerar PDF do Pedido", type="primary"):
    if not codigo_sel or not nome_cliente:
        st.error("Selecione o cliente antes de gerar.")
    elif not st.session_state.carrinho:
        st.error("Adicione ao menos uma amostra.")
    else:
        try:
            pdf_bytes = gerar_pdf(codigo_sel, nome_cliente, st.session_state.carrinho)
            st.success("PDF criado com sucesso!")
            st.download_button(
                label="📥 Baixar Pedido em PDF",
                data=pdf_bytes,
                file_name=f"pedido_{codigo_sel}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Erro ao gerar PDF: {e}")
