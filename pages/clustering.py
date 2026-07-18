# pyrefly: ignore [missing-import]
import html
from pathlib import Path

import pandas as pd

# pyrefly: ignore [missing-import]
import plotly.express as px
import requests
# pyrefly: ignore [missing-import]
import streamlit as st

from analytics.clustering import FEATURES_PADRAO, pipeline_completo

#Configuração da página 

st.set_page_config(
    layout="wide",
    page_title="Segmentação de clientes",
    page_icon="🤖",
    initial_sidebar_state="collapsed",
)

DATA_URL = "https://labdados.com/produtos"

TEMA_ESCURO = st.context.theme.type == "dark"

PALETA_CLUSTERS = (
    ["rgb(94, 196, 229)", "rgb(240, 138, 125)", "rgb(227, 180, 92)", "rgb(107, 203, 131)",
     "rgb(85, 199, 192)", "rgb(145, 164, 255)", "rgb(197, 148, 213)", "rgb(220, 141, 184)"]
    if TEMA_ESCURO else
    ["rgb(0, 103, 139)", "rgb(168, 77, 67)", "rgb(152, 105, 0)", "rgb(45, 122, 66)",
     "rgb(0, 125, 120)", "rgb(78, 99, 169)", "rgb(121, 80, 138)", "rgb(142, 70, 107)"]
)

CONFIG_GRAFICOS = {
    "displaylogo": False,
    "responsive": True,
    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
}

CATEGORIAS = {
    "brinquedos": "Brinquedos",
    "eletrodomesticos": "Eletrodomésticos",
    "eletronicos": "Eletrônicos",
    "esporte e lazer": "Esporte e lazer",
    "instrumentos musicais": "Instrumentos musicais",
    "livros": "Livros",
    "moveis": "Móveis",
    "utilidades domesticas": "Utilidades domésticas",
}

PAGAMENTOS = {
    "boleto": "Boleto",
    "cartao_credito": "Cartão de crédito",
    "cartao_debito": "Cartão de débito",
    "cupom": "Cupom",
}


#Funções auxiliares 


def _carrega_estilos() -> str:
    css = Path("assets/styles.css").read_text(encoding="utf-8")
    return f"<style>\n{css}\n</style>"


def formata_decimal(valor, casas=2):
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def formata_inteiro(valor):
    return f"{int(valor):,}".replace(",", ".")


def formata_moeda(valor, compacta=False):
    if compacta and abs(valor) >= 1_000_000:
        return f"R$ {formata_decimal(valor / 1_000_000)} mi"
    if compacta and abs(valor) >= 1_000:
        return f"R$ {formata_decimal(valor / 1_000, 1)} mil"
    return f"R$ {formata_decimal(valor)}"


def estiliza_grafico(figura, altura=420):
    figura.update_layout(
        height=altura,
        paper_bgcolor="rgba(0, 0, 0, 0)",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        font=dict(size=12),
        title=dict(
            font=dict(size=17),
            x=0.035,
            xanchor="left",
            y=0.96,
            yanchor="top",
        ),
        margin=dict(t=70, r=30, b=42, l=46),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="right",
            x=1,
        ),
    )
    figura.update_xaxes(zeroline=False, showline=False)
    figura.update_yaxes(zeroline=False, showline=False)
    return figura


#Carregamento de dados 


@st.cache_data(ttl=3600, show_spinner=False)
def carrega_dados():
    response = requests.get(DATA_URL, timeout=20)
    response.raise_for_status()
    dados = response.json()
    produtos = pd.DataFrame.from_dict(dados)
    produtos["Data da Compra"] = pd.to_datetime(
        produtos["Data da Compra"], format="%d/%m/%Y", errors="raise"
    )
    produtos["Categoria do Produto"] = (
        produtos["Categoria do Produto"]
        .map(CATEGORIAS)
        .fillna(produtos["Categoria do Produto"].str.capitalize())
    )
    produtos["Tipo de pagamento"] = (
        produtos["Tipo de pagamento"]
        .map(PAGAMENTOS)
        .fillna(produtos["Tipo de pagamento"].str.replace("_", " ").str.capitalize())
    )
    return produtos


@st.cache_data(ttl=3600, show_spinner="Rodando clusterização...")
def roda_clustering(df_json, n_clusters, features_tuple):
    """Recebe o JSON serializado e uma tupla de features para funcionar com st.cache_data."""
    from io import StringIO
    df = pd.read_json(StringIO(df_json))
    return pipeline_completo(
        df, n_clusters=n_clusters, features=list(features_tuple),
        calcular_elbow=True, k_max_elbow=10,
    )


# CSS e dados 

st.markdown(_carrega_estilos(), unsafe_allow_html=True)

try:
    produtos = carrega_dados()
except (requests.RequestException, ValueError, TypeError) as erro:
    st.error("Não foi possível carregar os dados de vendas agora.")
    if st.button("Tentar novamente", type="primary"):
        st.cache_data.clear()
        st.rerun()
    st.stop()


# Cabeçalho

st.markdown(
    """
    <header class="page-hero">
        <div>
            <h1>Segmentação de clientes</h1>
            <p>
                Agrupamento de compradores por perfil de compra usando K-Means.
                Cada transação é tratada como um cliente individual, segmentado
                por preço, frete, parcelas e avaliação.
            </p>
        </div>
    </header>
    """,
    unsafe_allow_html=True,
)


# Controles

# Todas as colunas numéricas que fazem sentido para clustering
FEATURES_DISPONIVEIS = [
    "Preço",
    "Frete",
    "Quantidade de parcelas",
    "Avaliação da compra",
    "Categoria do Produto",
    "Vendedor"
]

col_slider, col_features = st.columns([1, 3])

with col_slider:
    n_clusters = st.slider(
        "Número de clusters (k)",
        min_value=2,
        max_value=10,
        value=4,
        help="Escolha o número de segmentos de clientes.",
    )

with col_features:
    features_selecionadas = st.multiselect(
        "Features do modelo",
        options=FEATURES_DISPONIVEIS,
        default=FEATURES_PADRAO,
        help="Selecione quais variáveis o K-Means usará para agrupar os clientes.",
    )

# Precisa de pelo menos 2 features para o K-Means funcionar
if len(features_selecionadas) < 2:
    st.warning("Selecione pelo menos 2 features para rodar a clusterização.")
    st.stop()


# Executar clustering
# Converte para tupla porque st.cache_data não aceita listas como argumento (não são hashable)

with st.spinner("Calculando segmentação..."):
    resultado = roda_clustering(
        produtos.to_json(), n_clusters, tuple(features_selecionadas)
    )

df_clust = resultado["df_clusterizado"]
resumo = resultado["resumo_clusters"]
elbow = resultado["metricas_elbow"]


# KPIs

n_total = resultado["n_transacoes"]
maior_cluster = resumo.iloc[0]  # já ordenado por ticket

kpi_cols = st.columns(4)
kpi_cols[0].metric("Transações analisadas", formata_inteiro(n_total))
kpi_cols[1].metric("Clusters gerados", n_clusters)
kpi_cols[2].metric("Maior cluster", f"{resumo.loc[resumo['Vendas'].idxmax(), 'Cluster']}")
kpi_cols[3].metric(
    "Silhouette Score",
    formata_decimal(elbow.loc[elbow["k"] == n_clusters, "silhouette"].values[0], 3)
    if elbow is not None else "—",
)


#Gráficos 

st.markdown("---")

col_dist, col_elbow = st.columns(2, gap="medium")

# Distribuição dos clusters
with col_dist:
    fig_dist = px.pie(
        resumo,
        values="Vendas",
        names="Cluster",
        title="Distribuição de clientes por cluster",
        color_discrete_sequence=PALETA_CLUSTERS,
        hole=0.45,
    )
    fig_dist.update_traces(
        textinfo="percent+label",
        textposition="outside",
        hovertemplate="<b>%{label}</b><br>%{value:,} vendas (%{percent})<extra></extra>",
    )
    estiliza_grafico(fig_dist, altura=400)
    st.plotly_chart(fig_dist, use_container_width=True, config=CONFIG_GRAFICOS)

# Curva do Cotovelo
with col_elbow:
    if elbow is not None:
        fig_elbow = px.line(
            elbow,
            x="k",
            y="silhouette",
            markers=True,
            title="Silhouette Score por número de clusters",
        )
        fig_elbow.update_traces(
            line_color=PALETA_CLUSTERS[0],
            marker=dict(size=8),
        )
        # Destacar o k atual
        fig_elbow.add_vline(
            x=n_clusters,
            line_dash="dash",
            line_color=PALETA_CLUSTERS[1],
            annotation_text=f"k={n_clusters}",
            annotation_position="top",
        )
        fig_elbow.update_xaxes(title="k (número de clusters)", dtick=1)
        fig_elbow.update_yaxes(title="Silhouette Score")
        estiliza_grafico(fig_elbow, altura=400)
        st.plotly_chart(fig_elbow, use_container_width=True, config=CONFIG_GRAFICOS)


# Ticket médio por cluster
fig_ticket = px.bar(
    resumo.sort_values("Ticket_Médio", ascending=True),
    x="Ticket_Médio",
    y="Cluster",
    orientation="h",
    title="Ticket médio por cluster",
    color="Cluster",
    color_discrete_sequence=PALETA_CLUSTERS,
    text=resumo.sort_values("Ticket_Médio", ascending=True)["Ticket_Médio"].map(
        lambda v: formata_moeda(v, compacta=True)
    ),
)
fig_ticket.update_traces(
    textposition="outside",
    cliponaxis=False,
    showlegend=False,
)
fig_ticket.update_xaxes(title="Ticket Médio (R$)", showticklabels=False, gridcolor="rgba(0,0,0,0)")
fig_ticket.update_yaxes(title="")
estiliza_grafico(fig_ticket, altura=350)
st.plotly_chart(fig_ticket, use_container_width=True, config=CONFIG_GRAFICOS)


# Scatter: Preço x Parcelas colorido por cluster
fig_scatter = px.scatter(
    df_clust,
    x="Preço",
    y="Quantidade de parcelas",
    color="Cluster_label",
    color_discrete_sequence=PALETA_CLUSTERS,
    hover_name="Produto" if "Produto" in df_clust.columns else None,
    hover_data={"Preço": ":.2f", "Quantidade de parcelas": True, "Cluster_label": True},
    title="Preço × Parcelas por cluster",
    render_mode="webgl",
)
fig_scatter.update_traces(marker=dict(size=5, opacity=0.5))
fig_scatter.update_xaxes(title="Preço (R$)")
fig_scatter.update_yaxes(title="Parcelas", dtick=2)
estiliza_grafico(fig_scatter, altura=480)
st.plotly_chart(fig_scatter, use_container_width=True, config=CONFIG_GRAFICOS)


# Tabela resumo 

st.markdown("---")
st.markdown(
    """
    <div class="section-intro">
        <h2>Perfil detalhado de cada cluster</h2>
        <p>Métricas agregadas por segmento de cliente.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.dataframe(
    resumo,
    hide_index=True,
    use_container_width=True,
    column_config={
        "Cluster": st.column_config.TextColumn("Cluster", width="medium"),
        "Vendas": st.column_config.NumberColumn("Vendas", format="%d"),
        "Receita_Total": st.column_config.NumberColumn("Receita Total", format="R$ %.2f"),
        "Ticket_Médio": st.column_config.NumberColumn("Ticket Médio", format="R$ %.2f"),
        "Frete_Médio": st.column_config.NumberColumn("Frete Médio", format="R$ %.2f"),
        "Parcelas_Médias": st.column_config.NumberColumn("Parcelas Médias", format="%.1f"),
        "Avaliação_Média": st.column_config.NumberColumn("Avaliação Média", format="%.2f / 5"),
        "Estados": st.column_config.TextColumn("Estados presentes", width="large"),
        "Categorias": st.column_config.TextColumn("Top categorias", width="large"),
    },
)