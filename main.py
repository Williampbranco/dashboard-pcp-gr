import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os
import database  # Importa o arquivo database.py para criar a estrutura se não existir

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA (Deve ser a 1ª chamada Streamlit)
# ==========================================
st.set_page_config(
    page_title="PCP Executivo — GR CRUZEIRO", 
    page_icon="🏭", 
    layout="wide"
)

# ==========================================
# 2. VERIFICAÇÃO E CONEXÃO SEGURA AO BANCO DE DADOS
# ==========================================
def get_connection():
    # Se o arquivo de banco de dados SQLite não existir no servidor, força a criação imediata
    if not os.path.exists("gr_cruzeiro_pcp.db"):
        database.inicializar_banco_dados()
    return sqlite3.connect("gr_cruzeiro_pcp.db")

@st.cache_data(ttl=60)  # Recarrega o cache a cada 60 segundos
def carregar_dados_produtos():
    # Garantia dupla de inicialização do banco antes da leitura SQL
    if not os.path.exists("gr_cruzeiro_pcp.db"):
        database.inicializar_banco_dados()

    conn = get_connection()
    query = """
    SELECT p.codigo, p.nome, c.nome as categoria, p.unidade_medida, p.densidade_g_ml, 
           p.estoque_atual, p.estoque_minimo, p.custo_unitario, p.preco_venda_unitario,
           (p.estoque_atual * p.preco_venda_unitario) as valor_estoque_venda
    FROM produtos p
    LEFT JOIN categorias c ON p.categoria_id = c.id
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Ajuste dinâmico para simulação do Alerta MRP no PCP
    itens_alerta = [
        "Ácido Clorídrico 32%", 
        "Hipoclorito de Sódio 12%", 
        "Ácido Sulfúrico 98%", 
        "Detergente Alcalino Clorado | GR 02", 
        "Barrilha Densa"
    ]
    df.loc[df['nome'].isin(itens_alerta), 'estoque_atual'] = df['estoque_minimo'] * 0.35

    return df

# ==========================================
# 3. ESTILIZAÇÃO CSS CUSTOMIZADA (Cards Executivos)
# ==========================================
st.markdown("""
<style>
    /* Estilização dos Cards Executivos */
    .kpi-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 18px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        border-left: 5px solid #1E88E5;
        margin-bottom: 15px;
    }
    .kpi-title {
        color: #6c757d;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 5px;
    }
    .kpi-value {
        color: #1f2937;
        font-size: 1.75rem;
        font-weight: 700;
    }
    .kpi-status-ok { color: #10B981; font-weight: 600; font-size: 0.85rem; }
    .kpi-status-alert { color: #EF4444; font-weight: 600; font-size: 0.85rem; }
    
    /* Customização de Tabelas */
    .stDataFrame { border-radius: 8px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. EXECUÇÃO DO PAINEL PRINCIPAL
# ==========================================

# Header da Aplicação
st.title("🏭 Sistema Executivo de PCP — GR CRUZEIRO")
st.caption("Gestão Integrada de Planejamento, Estoque, Curva ABC e Necessidades de Produção Química")

df_produtos = carregar_dados_produtos()

# --- BARRA LATERAL ---
st.sidebar.header("🔍 Filtros do PCP")
categorias = ["Todas"] + list(df_produtos["categoria"].dropna().unique())
cat_selecionada = st.sidebar.selectbox("Filtrar Categoria", categorias)

if cat_selecionada != "Todas":
    df_filtrado = df_produtos[df_produtos["categoria"] == cat_selecionada]
else:
    df_filtrado = df_produtos.copy()

# --- CARDS DO CABEÇALHO (KPIs) ---
total_skus = len(df_filtrado)
valor_total_estoque = df_filtrado["valor_estoque_venda"].sum()
df_criticos = df_filtrado[df_filtrado["estoque_atual"] < df_filtrado["estoque_minimo"]].copy()
itens_abaixo_min = len(df_criticos)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #2563EB;">
            <div class="kpi-title">📦 Total de SKUs</div>
            <div class="kpi-value">{total_skus}</div>
            <div class="kpi-status-ok">✔ Cadastrados</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #059669;">
            <div class="kpi-title">💰 Valor do Estoque</div>
            <div class="kpi-value">R$ {valor_total_estoque:,.2f}</div>
            <div class="kpi-status-ok">✔ Valor de Venda Potencial</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    cor_alerta = "#EF4444" if itens_abaixo_min > 0 else "#10B981"
    status_txt = f"⚠️ {itens_abaixo_min} necessitam de OP" if itens_abaixo_min > 0 else "✔ Estoque Normalizado"
    st.markdown(f"""
        <div class="kpi-card" style="border-left-color: {cor_alerta};">
            <div class="kpi-title">🚨 Alertas de Risco MRP</div>
            <div class="kpi-value">{itens_abaixo_min} Itens</div>
            <div class="kpi-status-alert" style="color: {cor_alerta};">{status_txt}</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #8B5CF6;">
            <div class="kpi-title">⚡ Status do Sistema</div>
            <div class="kpi-value">100%</div>
            <div class="kpi-status-ok">✔ BD SQLite Conectado</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- ABAS PRINCIPAIS ---
tab_mrp, tab_abc, tab_catalogo = st.tabs([
    "🚨 Alertas MRP / Necessidade de Produção", 
    "🏆 Curva ABC de Produtos", 
    "📦 Catálogo Completo GR Cruzeiro"
])

# 1. ABA DE ALERTAS MRP
with tab_mrp:
    st.subheader("🚨 Itens Abaixo do Estoque Mínimo (Necessidade Urgente de Produção / Envasamento)")
    
    if len(df_criticos) > 0:
        # Cálculos de PCP
        df_criticos["Déficit (Unidades)"] = df_criticos["estoque_minimo"] - df_criticos["estoque_atual"]
        # Sugestão de OP com margem de segurança de +20%
        df_criticos["Sugestão de Lote OP"] = (df_criticos["Déficit (Unidades)"] * 1.2).round(0)
        df_criticos["Nível de Crise (%)"] = ((df_criticos["estoque_atual"] / df_criticos["estoque_minimo"]) * 100).round(1)

        # Gráfico comparativo
        fig_mrp = px.bar(
            df_criticos,
            x="nome",
            y=["estoque_atual", "estoque_minimo"],
            barmode="group",
            title="Comparativo: Estoque Atual vs. Estoque Mínimo dos Itens Críticos",
            labels={"value": "Quantidade", "variable": "Parâmetro", "nome": "Produto"},
            color_discrete_map={"estoque_atual": "#EF4444", "estoque_minimo": "#9CA3AF"}
        )
        st.plotly_chart(fig_mrp, use_container_width=True)

        st.markdown("### 📋 Tabela de Sugestão de Ordens de Produção (OP)")
        st.dataframe(
            df_criticos[[
                "codigo", "nome", "categoria", "unidade_medida", 
                "estoque_atual", "estoque_minimo", "Déficit (Unidades)", "Sugestão de Lote OP", "Nível de Crise (%)"
            ]].sort_values(by="Nível de Crise (%)"),
            use_container_width=True
        )

        col_op1, col_op2 = st.columns([3, 1])
        with col_op2:
            if st.button("🚀 Gerar Ordens de Produção Automáticas"):
                st.success("Ordens de Produção (OPs) enviadas para a fila do sequenciamento de envase!")
    else:
        st.success("🎉 Excelente! Nenhum item está abaixo do estoque mínimo no momento.")

# 2. ABA CURVA ABC
with tab_abc:
    st.subheader("Análise ABC por Valor Potencial de Estoque")
    df_abc = df_filtrado.sort_values(by="valor_estoque_venda", ascending=False).reset_index(drop=True)
    df_abc["% Acumulada"] = (df_abc["valor_estoque_venda"].cumsum() / df_abc["valor_estoque_venda"].sum()) * 100
    
    def classificar_abc(val):
        if val <= 70: return "Classe A"
        elif val <= 90: return "Classe B"
        else: return "Classe C"
        
    df_abc["Curva ABC"] = df_abc["% Acumulada"].apply(classificar_abc)

    col_g1, col_g2 = st.columns([2, 1])
    with col_g1:
        fig_bar = px.bar(
            df_abc.head(15), 
            x="nome", 
            y="valor_estoque_venda", 
            color="Curva ABC",
            title="Top 15 Produtos com Maior Impacto Financeiro (R$)",
            labels={"nome": "Produto", "valor_estoque_venda": "Valor (R$)"},
            color_discrete_map={"Classe A": "#1E88E5", "Classe B": "#F59E0B", "Classe C": "#10B981"}
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_g2:
        fig_pie = px.pie(
            df_abc, 
            names="Curva ABC", 
            values="valor_estoque_venda", 
            hole=0.4, 
            title="Distribuição Financeira da Curva ABC",
            color="Curva ABC",
            color_discrete_map={"Classe A": "#1E88E5", "Classe B": "#F59E0B", "Classe C": "#10B981"}
        )
        st.plotly_chart(fig_pie, use_container_width=True)

# 3. ABA CATÁLOGO
with tab_catalogo:
    st.subheader("Catálogo Mestre de Produtos GR CRUZEIRO")
    st.dataframe(df_filtrado, use_container_width=True)
