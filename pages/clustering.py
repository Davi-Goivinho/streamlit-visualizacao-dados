# pyrefly: ignore [missing-import]
from io import StringIO
from pathlib import Path

import pandas as pd

# pyrefly: ignore [missing-import]
import plotly.express as px
import requests

# pyrefly: ignore [missing-import]
import streamlit as st

from analytics.clustering import FEATURES_PADRAO, pipeline_completo
from analytics.clustering_kproto import (
    FEATURES_CATEGORICAS,
    FEATURES_NUMERICAS,
    analisa_resumo,
    executa_kprototypes,
)

# ── Configuração da página ──────────────────────────────────────────────────

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

# Opções disponíveis para cada tipo de filtro
FEATURES_NUMERICAS_DISPONIVEIS = [
    "Preço",
    "Frete",
    "Quantidade de parcelas",
    "Avaliação da compra",
]

FEATURES_CATEGORICAS_DISPONIVEIS = [
    "Categoria do Produto",
    "Tipo de pagamento",
]


# ── Funções auxiliares ──────────────────────────────────────────────────────


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


def render_avaliacoes_juntas(elbow_km, elbow_kp, n_clusters):
    if elbow_km is None or elbow_kp is None:
        return
        
    st.markdown("---")
    st.markdown("#### 📏 Como escolher o melhor número de clusters (k)?")
    st.info("💡 **Dicas de Leitura:**\n"
            "* **Custo (Elbow):** Procure a 'quina' (cotovelo) onde a curva para de cair drasticamente.\n"
            "* **Silhouette Score:** Procure o **maior pico**.\n"
            "* **Atenção:** O K-Prototypes não usa Silhouette porque a fórmula não funciona matematicamente para dados em texto. Use apenas o Custo Misto para avaliá-lo.")
            
    c1, c2, c3 = st.columns(3, gap="medium")
    
    with c1:
        fig_inercia = px.line(elbow_km, x="k", y="inercia", markers=True, title="K-Means: Custo (Elbow)")
        fig_inercia.update_traces(line_color=PALETA_CLUSTERS[0], marker=dict(size=8))
        fig_inercia.add_vline(x=n_clusters, line_dash="dash", line_color=PALETA_CLUSTERS[1], annotation_text=f"k={n_clusters}")
        fig_inercia.update_xaxes(title="k (número de clusters)", dtick=1)
        fig_inercia.update_yaxes(title="Inércia")
        estiliza_grafico(fig_inercia, altura=350)
        st.plotly_chart(fig_inercia, use_container_width=True, config=CONFIG_GRAFICOS)
        
    with c2:
        fig_sil = px.line(elbow_km, x="k", y="silhouette", markers=True, title="K-Means: Silhouette Score")
        fig_sil.update_traces(line_color=PALETA_CLUSTERS[2], marker=dict(size=8))
        fig_sil.add_vline(x=n_clusters, line_dash="dash", line_color=PALETA_CLUSTERS[1], annotation_text=f"k={n_clusters}")
        fig_sil.update_xaxes(title="k (número de clusters)", dtick=1)
        fig_sil.update_yaxes(title="Silhouette Score")
        estiliza_grafico(fig_sil, altura=350)
        st.plotly_chart(fig_sil, use_container_width=True, config=CONFIG_GRAFICOS)
        
    with c3:
        fig_cost = px.line(elbow_kp, x="k", y="cost", markers=True, title="K-Prototypes: Custo Misto (Elbow)")
        fig_cost.update_traces(line_color=PALETA_CLUSTERS[3], marker=dict(size=8))
        fig_cost.add_vline(x=n_clusters, line_dash="dash", line_color=PALETA_CLUSTERS[1], annotation_text=f"k={n_clusters}")
        fig_cost.update_xaxes(title="k (número de clusters)", dtick=1)
        fig_cost.update_yaxes(title="Custo Misto (Inércia)")
        estiliza_grafico(fig_cost, altura=350)
        st.plotly_chart(fig_cost, use_container_width=True, config=CONFIG_GRAFICOS)

def render_graficos(df_clust, resumo, sufixo=""):
    """
    Renderiza os gráficos que demonstram os clusters (donut, ticket, scatter).
    """
    col_dist, col_ticket = st.columns(2, gap="medium")

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

    with col_ticket:
        resumo_ticket = resumo.sort_values("Ticket_Médio", ascending=True)
        fig_ticket = px.bar(
            resumo_ticket,
            x="Ticket_Médio",
            y="Cluster",
            orientation="h",
            title="Ticket médio por cluster",
            color="Cluster",
            color_discrete_sequence=PALETA_CLUSTERS,
            text=resumo_ticket["Ticket_Médio"].map(lambda v: formata_moeda(v, compacta=True)),
        )
        fig_ticket.update_traces(textposition="outside", cliponaxis=False, showlegend=False)
        fig_ticket.update_xaxes(title="Ticket Médio (R$)", showticklabels=False, gridcolor="rgba(0,0,0,0)")
        fig_ticket.update_yaxes(title="")
        estiliza_grafico(fig_ticket, altura=400)
        st.plotly_chart(fig_ticket, use_container_width=True, config=CONFIG_GRAFICOS)

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


def render_tabela_kmeans(resumo):
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


def render_tabela_kproto(resumo):
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
            "Moda_Categoria": st.column_config.TextColumn("Categoria principal"),
            "Moda_Pagamento": st.column_config.TextColumn("Pagamento principal"),
            "Top_Estados": st.column_config.TextColumn("Top 3 estados", width="large"),
        },
    )


# ── Funções de cache ────────────────────────────────────────────────────────


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


@st.cache_data(ttl=3600, show_spinner=False)
def roda_kmeans(df_json, n_clusters, features_tuple):
    """K-Means: apenas features numéricas."""
    df = pd.read_json(StringIO(df_json))
    return pipeline_completo(
        df, n_clusters=n_clusters, features=list(features_tuple),
        calcular_elbow=True, k_max_elbow=10,
    )


@st.cache_data(ttl=3600, show_spinner=False)
def roda_kproto(df_json, n_clusters, feat_num_tuple, feat_cat_tuple):
    """K-Prototypes: features numéricas + categóricas."""
    import warnings
    from sklearn.preprocessing import StandardScaler
    from kmodes.kprototypes import KPrototypes
    from analytics.clustering_kproto import analisa_resumo

    df = pd.read_json(StringIO(df_json))

    feat_num = list(feat_num_tuple)
    feat_cat = list(feat_cat_tuple)
    feat_tudo = feat_num + feat_cat

    df_limpo = df.dropna(subset=feat_tudo).copy()
    df_modelo = df_limpo[feat_tudo].copy()

    scaler = StandardScaler()
    df_modelo[feat_num] = scaler.fit_transform(df_modelo[feat_num])

    indices_categoricos = [df_modelo.columns.get_loc(c) for c in feat_cat]

    kproto = KPrototypes(n_clusters=n_clusters, init="Cao", random_state=42, n_init=3)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        clusters = kproto.fit_predict(df_modelo.values, categorical=indices_categoricos)

    df_limpo = df_limpo.copy()
    df_limpo["Cluster"] = (clusters + 1).astype(str)
    df_limpo["Cluster_label"] = df_limpo["Cluster"].map(lambda c: f"Grupo {c}")

    resumo = analisa_resumo(df_limpo)

    # Curva real de Custo do K-Prototypes
    # O kmodes.KPrototypes fornece a propriedade .cost_ que soma a distância
    # euclidiana (numérica) com a penalidade categórica (dissimilaridade).
    # Como isso demora um pouco, usamos n_init=1 e n_jobs=-1 para acelerar.
    elbow_kp = []
    k_min, k_max = 2, min(8, len(df_limpo) - 1)  # limite k=8 por performance
    for k in range(k_min, k_max + 1):
        if k == n_clusters:
            custo = kproto.cost_
        else:
            kp_proxy = KPrototypes(n_clusters=k, init="Cao", random_state=42, n_init=1, n_jobs=-1)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                kp_proxy.fit(df_modelo.values, categorical=indices_categoricos)
            custo = kp_proxy.cost_
        elbow_kp.append({"k": k, "cost": custo})
    
    df_elbow_kp = pd.DataFrame(elbow_kp)
    custo_atual = kproto.cost_

    return {
        "df_clusterizado": df_limpo,
        "resumo_clusters": resumo,
        "cost_kp": custo_atual,
        "metricas_elbow": df_elbow_kp,
    }


# ── Página ──────────────────────────────────────────────────────────────────

st.markdown(_carrega_estilos(), unsafe_allow_html=True)

try:
    produtos = carrega_dados()
except (requests.RequestException, ValueError, TypeError):
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
                Comparativo entre K-Means (variáveis numéricas) e K-Prototypes
                (variáveis numéricas + categóricas). Ambos os modelos compartilham
                o mesmo número de clusters e as mesmas métricas numéricas.
            </p>
        </div>
    </header>
    """,
    unsafe_allow_html=True,
)


# ── Controles ───────────────────────────────────────────────────────────────

st.markdown("### ⚙️ Parâmetros do modelo")
st.caption(
    "O **número de clusters** e as **métricas numéricas** se aplicam a ambos os modelos. "
    "As **variáveis categóricas** são exclusivas do K-Prototypes."
)

col_slider, col_num, col_cat = st.columns([1, 2, 2])

with col_slider:
    n_clusters = st.slider(
        "Número de clusters (k)",
        min_value=2,
        max_value=10,
        value=4,
        help="Aplica-se ao K-Means e ao K-Prototypes.",
    )

with col_num:
    feat_num = st.multiselect(
        "Métricas numéricas",
        options=FEATURES_NUMERICAS_DISPONIVEIS,
        default=FEATURES_NUMERICAS_DISPONIVEIS,
        help="Usadas por ambos os modelos (K-Means e K-Prototypes).",
    )

with col_cat:
    feat_cat = st.multiselect(
        "Variáveis categóricas (K-Prototypes)",
        options=FEATURES_CATEGORICAS_DISPONIVEIS,
        default=FEATURES_CATEGORICAS_DISPONIVEIS,
        help="Exclusivas do K-Prototypes. O K-Means ignora estas colunas.",
    )

if len(feat_num) < 2:
    st.warning("Selecione pelo menos 2 métricas numéricas.")
    st.stop()

if len(feat_cat) < 1:
    st.warning("Selecione pelo menos 1 variável categórica para o K-Prototypes.")
    st.stop()

df_json = produtos.to_json()

# ── Indicadores de Custo (Elbow) & Silhouette Score ambos modelors 

with st.spinner("Treinando K-Means e K-Prototypes... (pode demorar alguns segundos)"):
    res_km = roda_kmeans(df_json, n_clusters, tuple(feat_num))
    res_kp = roda_kproto(df_json, n_clusters, tuple(feat_num), tuple(feat_cat))

df_km = res_km["df_clusterizado"]
resumo_km = res_km["resumo_clusters"]
elbow_km = res_km["metricas_elbow"]

df_kp = res_kp["df_clusterizado"]
resumo_kp = res_kp["resumo_clusters"]
elbow_kp = res_kp["metricas_elbow"]
cost_kp = res_kp["cost_kp"]

render_avaliacoes_juntas(elbow_km, elbow_kp, n_clusters)

# ── Seção K-Means ────────────────────────────────────────────────────────────

st.markdown("---")
st.markdown(
    """
    <div class="section-intro">
        <h2>K-Means — Clustering por métricas numéricas</h2>
        <p>
            Segmenta os compradores usando apenas variáveis numéricas normalizadas
            (StandardScaler). Simples, rápido e interpretável.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# KPIs do K-Means
kpi_cols = st.columns(4)
kpi_cols[0].metric("Transações", formata_inteiro(res_km["n_transacoes"]))
kpi_cols[1].metric("Clusters", n_clusters)
kpi_cols[2].metric("Maior grupo", resumo_km.loc[resumo_km["Vendas"].idxmax(), "Cluster"])
kpi_cols[3].metric(
    "Silhouette Score",
    formata_decimal(
        elbow_km.loc[elbow_km["k"] == n_clusters, "silhouette"].values[0], 3
    ) if elbow_km is not None else "—",
)

st.markdown("#### Distribuição e Características dos Clusters")
render_graficos(df_km, resumo_km, sufixo="_km")

st.markdown("#### Perfil detalhado — K-Means")
render_tabela_kmeans(resumo_km)


# ── Seção K-Prototypes ───────────────────────────────────────────────────────

st.markdown("---")
st.markdown(
    """
    <div class="section-intro">
        <h2>K-Prototypes — Clustering por dados mistos</h2>
        <p>
            Combina distância euclidiana (variáveis numéricas) com dissimilaridade
            por correspondência (variáveis categóricas). Nenhum One-Hot Encoding necessário.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# KPIs do K-Prototypes
kpi_cols2 = st.columns(4)
kpi_cols2[0].metric("Transações", formata_inteiro(len(df_kp)))
kpi_cols2[1].metric("Clusters", n_clusters)
kpi_cols2[2].metric("Maior grupo", resumo_kp.loc[resumo_kp["Vendas"].idxmax(), "Cluster"])
kpi_cols2[3].metric(
    "Custo Total (Inércia)",
    formata_inteiro(cost_kp),
    help="Métrica de custo nativa do K-Prototypes (soma da distância numérica + dissimilaridade categórica).",
)

st.markdown("#### Distribuição e Características dos Clusters")
render_graficos(df_kp, resumo_kp, sufixo="_kp")

st.markdown("#### Perfil detalhado — K-Prototypes")
render_tabela_kproto(resumo_kp)

st.caption(
    "K-Means: scikit-learn · K-Prototypes: kmodes — "
    "Clusters ordenados por ticket médio crescente (Grupo 1 = menor ticket)."
)