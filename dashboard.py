# pyrefly: ignore [missing-import]
import html

import pandas as pd

# pyrefly: ignore [missing-import]
import plotly.express as px

# pyrefly: ignore [missing-import]
import plotly.graph_objects as go

# pyrefly: ignore [missing-import]
from plotly.subplots import make_subplots
import requests
import streamlit as st


st.set_page_config(
    layout="wide",
    page_title="Visão de vendas",
    page_icon="📈",
    initial_sidebar_state="collapsed",
)


DATA_URL = "https://labdados.com/produtos"

# O Streamlit informa o tema ativo ao Python. As cores abaixo servem apenas às
# marcas dos gráficos; superfícies, textos e controles ficam a cargo do tema
# nativo para que a troca claro/escuro continue funcionando no navegador.
TEMA_ESCURO = st.context.theme.type == "dark"

if TEMA_ESCURO:
    COR_PRIMARIA = "rgb(114, 200, 232)"
    COR_PRIMARIA_MEDIA = "rgb(82, 177, 211)"
    COR_PRIMARIA_CLARA = "rgb(42, 111, 137)"
    COR_DESTAQUE = "rgb(240, 138, 125)"
    COR_DOURADA = "rgb(227, 180, 92)"
    COR_MAPA = "carto-darkmatter"
    COR_HEATMAP_INICIO = "rgb(27, 43, 50)"
    COR_TEXTO_CELULA_FRACA = "rgb(242, 247, 248)"
    COR_TEXTO_CELULA_FORTE = "rgb(14, 21, 25)"
    PALETA_CATEGORIAS = [
        "rgb(94, 196, 229)",
        "rgb(240, 138, 125)",
        "rgb(227, 180, 92)",
        "rgb(107, 203, 131)",
        "rgb(85, 199, 192)",
        "rgb(145, 164, 255)",
        "rgb(197, 148, 213)",
        "rgb(220, 141, 184)",
    ]
else:
    COR_PRIMARIA = "rgb(11, 93, 124)"
    COR_PRIMARIA_MEDIA = "rgb(18, 124, 163)"
    COR_PRIMARIA_CLARA = "rgb(119, 184, 215)"
    COR_DESTAQUE = "rgb(168, 77, 67)"
    COR_DOURADA = "rgb(152, 105, 0)"
    COR_MAPA = "carto-positron"
    COR_HEATMAP_INICIO = "rgb(240, 247, 250)"
    COR_TEXTO_CELULA_FRACA = "rgb(16, 33, 38)"
    COR_TEXTO_CELULA_FORTE = "rgb(255, 255, 255)"
    PALETA_CATEGORIAS = [
        "rgb(0, 103, 139)",
        "rgb(168, 77, 67)",
        "rgb(152, 105, 0)",
        "rgb(45, 122, 66)",
        "rgb(0, 125, 120)",
        "rgb(78, 99, 169)",
        "rgb(121, 80, 138)",
        "rgb(142, 70, 107)",
    ]

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

MESES = {
    1: "Jan",
    2: "Fev",
    3: "Mar",
    4: "Abr",
    5: "Mai",
    6: "Jun",
    7: "Jul",
    8: "Ago",
    9: "Set",
    10: "Out",
    11: "Nov",
    12: "Dez",
}


ESTILOS = """
<style>
[data-testid="stAppViewContainer"] {
    /* O Streamlit atualiza color-scheme ao trocar Claro/Escuro. */
    --ui-surface: light-dark(#f3f6f7, #172228);
    --ui-surface-strong: light-dark(#e8f1f4, #1d3039);
    --ui-muted: light-dark(#4b5f66, #b8c6cb);
    --ui-border: light-dark(#d1dcdf, #34474f);
}

.block-container {
    max-width: 1420px;
    padding: 2rem 2.25rem 5rem;
}

h1, h2, h3 {
    letter-spacing: -0.025em;
    text-wrap: balance;
}

p {
    text-wrap: pretty;
}

.page-hero {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 2rem;
    padding: 0.75rem 0 1.75rem;
    border-bottom: 1px solid var(--ui-border);
    margin-bottom: 1.25rem;
}

.page-hero h1 {
    font-size: 2.55rem;
    line-height: 1.05;
    font-weight: 720;
    letter-spacing: -0.035em;
    margin: 0 0 0.65rem;
}

.page-hero p {
    max-width: 68ch;
    color: var(--ui-muted);
    font-size: 1rem;
    line-height: 1.6;
    margin: 0;
}

.hero-meta {
    min-width: 15rem;
    text-align: right;
    font-size: 0.86rem;
    line-height: 1.55;
}

.hero-meta > div:not(:first-child) {
    color: var(--ui-muted);
}

.hero-meta strong {
    font-weight: 650;
}

.status-dot {
    display: inline-block;
    width: 0.48rem;
    height: 0.48rem;
    margin-right: 0.45rem;
    border-radius: 50%;
    background: currentColor;
    vertical-align: 0.06rem;
}

.st-key-filter_panel {
    background: var(--ui-surface);
    border: 1px solid var(--ui-border);
    border-radius: 12px;
    padding: 1rem 1.1rem 0.8rem;
    margin: 1.25rem 0 0.9rem;
}

.filter-heading {
    margin-bottom: 0.6rem;
}

.filter-heading strong {
    display: block;
    font-size: 1rem;
    margin-bottom: 0.15rem;
}

.filter-heading span {
    color: var(--ui-muted);
    font-size: 0.86rem;
}

[data-baseweb="select"] > div,
[data-baseweb="input"] {
    border-radius: 8px !important;
}

.result-line {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.45rem;
    font-size: 0.9rem;
    margin: 0.25rem 0 1.1rem;
}

.result-line > span:last-child {
    color: var(--ui-muted);
}

.result-line strong {
    font-weight: 650;
}

.kpi-strip {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    border-top: 1px solid var(--ui-border);
    border-bottom: 1px solid var(--ui-border);
    margin: 0.5rem 0 2rem;
}

.kpi-item {
    padding: 1.25rem 1.45rem 1.3rem;
    border-right: 1px solid var(--ui-border);
}

.kpi-item:first-child {
    padding-left: 0;
}

.kpi-item:last-child {
    border-right: 0;
}

.kpi-label {
    display: block;
    color: var(--ui-muted);
    font-size: 0.82rem;
    font-weight: 560;
    margin-bottom: 0.42rem;
}

.kpi-item dd {
    margin: 0;
}

.kpi-value {
    display: block;
    font-size: 1.72rem;
    line-height: 1.1;
    font-weight: 720;
    letter-spacing: -0.025em;
}

.kpi-note {
    display: block;
    color: var(--ui-muted);
    font-size: 0.75rem;
    margin-top: 0.38rem;
}

.section-intro {
    max-width: 72ch;
    margin: 2.1rem 0 0.9rem;
}

.section-intro h2 {
    font-size: 1.35rem;
    line-height: 1.25;
    margin: 0 0 0.35rem;
}

.section-intro p {
    color: var(--ui-muted);
    font-size: 0.91rem;
    line-height: 1.55;
    margin: 0;
}

.insight-note {
    background: var(--ui-surface-strong);
    border: 1px solid var(--ui-border);
    border-radius: 9px;
    padding: 0.85rem 1rem;
    margin: 1.25rem 0 0.4rem;
    font-size: 0.9rem;
    line-height: 1.55;
}

.insight-note strong {
    font-weight: 680;
}

[data-testid="stPlotlyChart"] {
    border: 1px solid var(--ui-border);
    border-radius: 12px;
    padding: 0.25rem 0.35rem 0;
    overflow: hidden;
}

[data-baseweb="tab-list"] {
    gap: 1.25rem;
}

button[data-baseweb="tab"] {
    min-height: 3rem;
    padding-left: 0;
    padding-right: 0;
    font-weight: 560;
}

.stButton button,
.stDownloadButton button {
    min-height: 44px;
    border-radius: 8px;
}

[data-testid="stDataFrame"] {
    border: 1px solid var(--ui-border);
    border-radius: 10px;
    overflow: hidden;
}

.data-note {
    font-size: 0.82rem;
    line-height: 1.5;
}

.data-note span {
    color: var(--ui-muted);
}

@media (max-width: 900px) {
    .block-container {
        padding: 1.4rem 1.25rem 4rem;
    }

    .page-hero {
        align-items: flex-start;
        flex-direction: column;
        gap: 1rem;
    }

    .hero-meta {
        min-width: 0;
        text-align: left;
    }

    .kpi-strip {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    .kpi-item:nth-child(2) {
        border-right: 0;
    }

    .kpi-item:nth-child(-n+2) {
        border-bottom: 1px solid var(--ui-border);
    }

    .kpi-item:nth-child(3) {
        padding-left: 0;
    }
}

@media (max-width: 560px) {
    .page-hero h1 {
        font-size: 2rem;
    }

    .kpi-strip {
        grid-template-columns: 1fr;
    }

    .kpi-item,
    .kpi-item:nth-child(3) {
        padding: 1rem 0;
        border-right: 0;
        border-bottom: 1px solid var(--ui-border);
    }

    .kpi-item:last-child {
        border-bottom: 0;
    }

    [data-baseweb="tab-list"] {
        gap: 0.85rem;
        overflow-x: auto;
    }
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        scroll-behavior: auto !important;
        transition-duration: 0.01ms !important;
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
    }
}
</style>
"""


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


def formata_mes(data):
    return f"{MESES[data.month]}/{data.year}"


def titulo_secao(titulo, descricao):
    st.markdown(
        f"""
        <div class="section-intro">
            <h2>{html.escape(titulo)}</h2>
            <p>{html.escape(descricao)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


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
    figura.update_xaxes(
        zeroline=False,
        showline=False,
    )
    figura.update_yaxes(
        zeroline=False,
        showline=False,
    )
    return figura


@st.cache_data(ttl=3600, show_spinner=False)
def carrega_dados():
    response = requests.get(DATA_URL, timeout=20)
    response.raise_for_status()
    dados = response.json()

    if not isinstance(dados, list) or not dados:
        raise ValueError("A API retornou uma base vazia ou em formato inesperado.")

    produtos = pd.DataFrame.from_dict(dados)
    colunas_obrigatorias = {
        "Produto",
        "Categoria do Produto",
        "Preço",
        "Frete",
        "Data da Compra",
        "Vendedor",
        "Local da compra",
        "Avaliação da compra",
        "Tipo de pagamento",
        "Quantidade de parcelas",
        "lat",
        "lon",
    }
    colunas_ausentes = colunas_obrigatorias.difference(produtos.columns)
    if colunas_ausentes:
        raise ValueError(
            "A API não retornou todas as colunas esperadas: "
            + ", ".join(sorted(colunas_ausentes))
        )

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


st.markdown(ESTILOS, unsafe_allow_html=True)

try:
    produtos = carrega_dados()
except (requests.RequestException, ValueError, TypeError) as erro:
    st.error("Não foi possível carregar os dados de vendas agora.")
    st.write(
        "A fonte pública pode estar temporariamente indisponível. "
        "Tente novamente sem perder esta página."
    )
    if st.button("Tentar novamente", type="primary"):
        st.cache_data.clear()
        st.rerun()
    with st.expander("Detalhes técnicos"):
        st.code(str(erro))
    st.stop()


data_minima = produtos["Data da Compra"].min().date()
data_maxima = produtos["Data da Compra"].max().date()
total_registros = len(produtos)

st.markdown(
    f"""
    <header class="page-hero">
        <div>
            <h1>Visão de vendas</h1>
            <p>
                Explore receita, volume e comportamento de compra em uma base
                pública de e-commerce brasileiro. Use os filtros para investigar
                um recorte e consulte as vendas individuais quando precisar.
            </p>
        </div>
        <div class="hero-meta">
            <div><span class="status-dot"></span><strong>Dados disponíveis</strong></div>
            <div>{data_minima:%d/%m/%Y} a {data_maxima:%d/%m/%Y}</div>
            <div>{formata_inteiro(total_registros)} transações · API LabDados</div>
        </div>
    </header>
    """,
    unsafe_allow_html=True,
)


def limpa_filtros():
    st.session_state["filtro_periodo"] = (data_minima, data_maxima)
    st.session_state["ultimo_periodo_valido"] = (data_minima, data_maxima)
    st.session_state["filtro_categorias"] = []
    st.session_state["filtro_ufs"] = []
    st.session_state["filtro_vendedores"] = []


if "ultimo_periodo_valido" not in st.session_state:
    st.session_state["ultimo_periodo_valido"] = (data_minima, data_maxima)
if "filtro_periodo" not in st.session_state:
    st.session_state["filtro_periodo"] = (data_minima, data_maxima)

with st.container(key="filter_panel"):
    st.markdown(
        """
        <div class="filter-heading">
            <strong>Refine a análise</strong>
            <span>Seleções vazias incluem todas as opções.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_periodo, col_categoria, col_uf, col_vendedor = st.columns(4, gap="small")

    with col_periodo:
        periodo = st.date_input(
            "Período da compra",
            min_value=data_minima,
            max_value=data_maxima,
            format="DD/MM/YYYY",
            key="filtro_periodo",
        )

    with col_categoria:
        categorias = st.multiselect(
            "Categoria",
            options=sorted(produtos["Categoria do Produto"].unique()),
            placeholder="Todas as categorias",
            key="filtro_categorias",
        )

    with col_uf:
        ufs = st.multiselect(
            "UF",
            options=sorted(produtos["Local da compra"].unique()),
            placeholder="Todos os estados",
            key="filtro_ufs",
        )

    with col_vendedor:
        vendedores = st.multiselect(
            "Vendedor",
            options=sorted(produtos["Vendedor"].unique()),
            placeholder="Todos os vendedores",
            key="filtro_vendedores",
        )

    ajuda_filtros, acao_filtros = st.columns([5, 1], vertical_alignment="center")
    with ajuda_filtros:
        st.caption("Os gráficos, a tabela e o CSV usam sempre o mesmo recorte.")
    with acao_filtros:
        st.button(
            "Limpar filtros", on_click=limpa_filtros, type="secondary", width="stretch"
        )


periodo_incompleto = not (isinstance(periodo, (tuple, list)) and len(periodo) == 2)
if periodo_incompleto:
    inicio, fim = st.session_state["ultimo_periodo_valido"]
    st.warning(
        "Selecione também a data final. Enquanto isso, mantivemos o último "
        "período completo para não alterar os resultados silenciosamente."
    )
else:
    inicio, fim = periodo
    st.session_state["ultimo_periodo_valido"] = (inicio, fim)

inicio_timestamp = pd.to_datetime(inicio)
fim_timestamp = pd.to_datetime(fim)

produtos_filtrados = produtos[
    (produtos["Data da Compra"] >= inicio_timestamp)
    & (produtos["Data da Compra"] <= fim_timestamp)
].copy()

if categorias:
    produtos_filtrados = produtos_filtrados[
        produtos_filtrados["Categoria do Produto"].isin(categorias)
    ]
if ufs:
    produtos_filtrados = produtos_filtrados[
        produtos_filtrados["Local da compra"].isin(ufs)
    ]
if vendedores:
    produtos_filtrados = produtos_filtrados[
        produtos_filtrados["Vendedor"].isin(vendedores)
    ]

filtros_ativos = []
if (inicio, fim) != (data_minima, data_maxima):
    filtros_ativos.append(f"{inicio:%d/%m/%Y}–{fim:%d/%m/%Y}")
if categorias:
    filtros_ativos.append(
        f"{len(categorias)} categoria" + ("s" if len(categorias) > 1 else "")
    )
if ufs:
    filtros_ativos.append(f"{len(ufs)} UF" + ("s" if len(ufs) > 1 else ""))
if vendedores:
    filtros_ativos.append(
        f"{len(vendedores)} vendedor" + ("es" if len(vendedores) > 1 else "")
    )

descricao_recorte = " · ".join(filtros_ativos) if filtros_ativos else "Base completa"
st.markdown(
    f"""
    <div class="result-line">
        <span class="status-dot"></span>
        <strong>{formata_inteiro(len(produtos_filtrados))} de {formata_inteiro(total_registros)} vendas</strong>
        <span>· {html.escape(descricao_recorte)}</span>
    </div>
    """,
    unsafe_allow_html=True,
)

if produtos_filtrados.empty:
    st.warning(
        "Nenhuma venda corresponde a este conjunto de filtros. "
        "Remova uma seleção ou volte para a base completa."
    )
    st.button("Voltar para a base completa", on_click=limpa_filtros, type="primary")
    st.stop()


receita_total = produtos_filtrados["Preço"].sum()
ticket_medio = produtos_filtrados["Preço"].mean()
frete_medio = produtos_filtrados["Frete"].mean()

st.markdown(
    f"""
    <dl class="kpi-strip" aria-label="Indicadores do recorte atual">
        <div class="kpi-item">
            <dt class="kpi-label">Vendas</dt>
            <dd class="kpi-value">{formata_inteiro(len(produtos_filtrados))}</dd>
            <dd class="kpi-note">transações no recorte</dd>
        </div>
        <div class="kpi-item">
            <dt class="kpi-label">Receita</dt>
            <dd class="kpi-value">{formata_moeda(receita_total, compacta=True)}</dd>
            <dd class="kpi-note">soma do preço dos produtos</dd>
        </div>
        <div class="kpi-item">
            <dt class="kpi-label">Ticket médio</dt>
            <dd class="kpi-value">{formata_moeda(ticket_medio)}</dd>
            <dd class="kpi-note">valor médio por transação</dd>
        </div>
        <div class="kpi-item">
            <dt class="kpi-label">Frete médio</dt>
            <dd class="kpi-value">{formata_moeda(frete_medio)}</dd>
            <dd class="kpi-note">frete não incluído na receita</dd>
        </div>
    </dl>
    """,
    unsafe_allow_html=True,
)


receita_localizacao = (
    produtos_filtrados.groupby("Local da compra")
    .agg(Receita=("Preço", "sum"), Vendas=("Preço", "size"))
    .reset_index()
    .rename(columns={"Local da compra": "UF"})
)
receita_localizacao["Receita formatada"] = receita_localizacao["Receita"].map(
    formata_moeda
)
receita_localizacao["Vendas formatadas"] = receita_localizacao["Vendas"].map(
    formata_inteiro
)

receita_mapa = (
    produtos_filtrados.groupby("Local da compra")
    .agg(
        Receita=("Preço", "sum"),
        Vendas=("Preço", "size"),
        lat=("lat", "first"),
        lon=("lon", "first"),
    )
    .reset_index()
    .rename(columns={"Local da compra": "UF"})
)
receita_mapa["Receita formatada"] = receita_mapa["Receita"].map(formata_moeda)
receita_mapa["Vendas formatadas"] = receita_mapa["Vendas"].map(formata_inteiro)

fig_mapa = px.scatter_map(
    receita_mapa,
    lat="lat",
    lon="lon",
    size="Receita",
    size_max=34,
    zoom=3.2,
    map_style=COR_MAPA,
    hover_name="UF",
    custom_data=["Receita formatada", "Vendas formatadas"],
    title="Distribuição geográfica da receita",
    color_discrete_sequence=[COR_PRIMARIA],
)
fig_mapa.update_traces(
    marker_opacity=0.78,
    hovertemplate=(
        "<b>%{hovertext}</b><br>%{customdata[0]}"
        "<br>%{customdata[1]} vendas<extra></extra>"
    ),
)
fig_mapa.update_layout(
    map=dict(center=dict(lat=-14.2350, lon=-51.9253)), uirevision="mapa-brasil"
)
estiliza_grafico(fig_mapa, altura=430)

top_estados = receita_localizacao.nlargest(10, "Receita").sort_values(
    "Receita", ascending=True
)
top_estados["Rótulo"] = top_estados["Receita"].map(
    lambda valor: formata_moeda(valor, compacta=True)
)
fig_estados = px.bar(
    top_estados,
    x="Receita",
    y="UF",
    orientation="h",
    text="Rótulo",
    custom_data=["Receita formatada", "Vendas formatadas"],
    title="10 estados com maior receita",
)
fig_estados.update_traces(
    marker_color=COR_PRIMARIA,
    textposition="outside",
    cliponaxis=False,
    hovertemplate=(
        "<b>%{y}</b><br>%{customdata[0]}<br>%{customdata[1]} vendas<extra></extra>"
    ),
)
fig_estados.update_xaxes(showticklabels=False, gridcolor="rgba(0, 0, 0, 0)")
fig_estados.update_yaxes(title="")
estiliza_grafico(fig_estados, altura=430)
fig_estados.update_layout(margin=dict(t=70, r=78, b=32, l=42))

vendas_mensais = (
    produtos_filtrados.groupby(produtos_filtrados["Data da Compra"].dt.to_period("M"))
    .agg(Receita=("Preço", "sum"), Vendas=("Preço", "size"))
    .reset_index()
)
vendas_mensais["Data da Compra"] = vendas_mensais["Data da Compra"].dt.to_timestamp()
vendas_mensais["Receita formatada"] = vendas_mensais["Receita"].map(formata_moeda)
vendas_mensais["Vendas formatadas"] = vendas_mensais["Vendas"].map(formata_inteiro)

fig_tendencia = make_subplots(
    rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.09, row_heights=[0.64, 0.36]
)
fig_tendencia.add_trace(
    go.Scatter(
        x=vendas_mensais["Data da Compra"],
        y=vendas_mensais["Receita"],
        customdata=vendas_mensais[["Receita formatada"]],
        name="Receita",
        mode="lines+markers",
        line=dict(color=COR_PRIMARIA, width=2.6),
        marker=dict(color=COR_PRIMARIA, size=5),
        hovertemplate="%{customdata[0]}<extra></extra>",
    ),
    row=1,
    col=1,
)
fig_tendencia.add_trace(
    go.Bar(
        x=vendas_mensais["Data da Compra"],
        y=vendas_mensais["Vendas"],
        customdata=vendas_mensais[["Vendas formatadas"]],
        name="Vendas",
        marker_color=COR_PRIMARIA_CLARA,
        hovertemplate="%{customdata[0]} vendas<extra></extra>",
    ),
    row=2,
    col=1,
)
fig_tendencia.update_layout(
    title="Receita e volume por mês", hovermode="x unified", bargap=0.22
)
fig_tendencia.update_yaxes(title_text="Receita (R$)", row=1, col=1)
fig_tendencia.update_yaxes(title_text="Vendas", row=2, col=1)
fig_tendencia.update_xaxes(title_text="", row=2, col=1)
estiliza_grafico(fig_tendencia, altura=520)

dados_heatmap = produtos_filtrados.assign(
    Ano=produtos_filtrados["Data da Compra"].dt.year,
    Mês=produtos_filtrados["Data da Compra"].dt.month,
)
heatmap_pivot = (
    dados_heatmap.groupby(["Ano", "Mês"])["Preço"]
    .sum()
    .reset_index()
    .pivot(index="Ano", columns="Mês", values="Preço")
    .fillna(0)
)
heatmap_pivot.columns = [
    MESES.get(coluna, str(coluna)) for coluna in heatmap_pivot.columns
]
heatmap_pivot.index = heatmap_pivot.index.astype(str)

fig_heatmap = px.imshow(
    heatmap_pivot,
    title="Sazonalidade da receita",
    color_continuous_scale=[
        [0, COR_HEATMAP_INICIO],
        [0.45, COR_PRIMARIA_CLARA],
        [1, COR_PRIMARIA],
    ],
    labels={"x": "Mês", "y": "Ano", "color": "Receita"},
    aspect="auto",
)
hover_heatmap = heatmap_pivot.map(formata_moeda).values
fig_heatmap.update_traces(
    customdata=hover_heatmap,
    hovertemplate="<b>%{y} · %{x}</b><br>%{customdata}<extra></extra>",
    xgap=4,
    ygap=4,
)
limite_texto_claro = heatmap_pivot.to_numpy().max() * 0.58
for indice_ano, ano in enumerate(heatmap_pivot.index):
    for indice_mes, mes in enumerate(heatmap_pivot.columns):
        valor = heatmap_pivot.iloc[indice_ano, indice_mes]
        fig_heatmap.add_annotation(
            x=mes,
            y=ano,
            text=formata_moeda(valor, compacta=True).replace("R$ ", ""),
            showarrow=False,
            font=dict(
                size=10,
                color=(
                    COR_TEXTO_CELULA_FORTE
                    if valor >= limite_texto_claro
                    else COR_TEXTO_CELULA_FRACA
                ),
            ),
        )
fig_heatmap.update_layout(coloraxis_colorbar=dict(title="Receita"))
estiliza_grafico(fig_heatmap, altura=360)

desempenho_vendedor = (
    produtos_filtrados.groupby("Vendedor")
    .agg(Receita=("Preço", "sum"), Vendas=("Preço", "size"))
    .reset_index()
    .sort_values("Receita", ascending=True)
)
desempenho_vendedor["Receita formatada"] = desempenho_vendedor["Receita"].map(
    formata_moeda
)
desempenho_vendedor["Vendas formatadas"] = desempenho_vendedor["Vendas"].map(
    formata_inteiro
)
desempenho_vendedor["Rótulo"] = desempenho_vendedor["Receita"].map(
    lambda valor: formata_moeda(valor, compacta=True)
)
fig_vendedores = px.bar(
    desempenho_vendedor,
    x="Receita",
    y="Vendedor",
    orientation="h",
    text="Rótulo",
    custom_data=["Receita formatada", "Vendas formatadas"],
    title="Receita por vendedor",
)
fig_vendedores.update_traces(
    marker_color=COR_PRIMARIA_MEDIA,
    textposition="outside",
    cliponaxis=False,
    hovertemplate=(
        "<b>%{y}</b><br>%{customdata[0]}<br>%{customdata[1]} vendas<extra></extra>"
    ),
)
fig_vendedores.update_xaxes(showticklabels=False, gridcolor="rgba(0, 0, 0, 0)")
fig_vendedores.update_yaxes(title="")
estiliza_grafico(fig_vendedores, altura=500)
fig_vendedores.update_layout(margin=dict(t=70, r=82, b=32, l=52))

avaliacao_categoria = (
    produtos_filtrados.groupby("Categoria do Produto")
    .agg(
        Avaliação=("Avaliação da compra", "mean"),
        Amostra=("Avaliação da compra", "size"),
    )
    .reset_index()
    .sort_values("Avaliação", ascending=True)
)
avaliacao_categoria["Rótulo"] = avaliacao_categoria.apply(
    lambda linha: (
        f"{formata_decimal(linha['Avaliação'])} · n={formata_inteiro(linha['Amostra'])}"
    ),
    axis=1,
)
avaliacao_categoria["Avaliação formatada"] = avaliacao_categoria["Avaliação"].map(
    formata_decimal
)
avaliacao_categoria["Amostra formatada"] = avaliacao_categoria["Amostra"].map(
    formata_inteiro
)
fig_avaliacao = px.bar(
    avaliacao_categoria,
    x="Avaliação",
    y="Categoria do Produto",
    orientation="h",
    text="Rótulo",
    custom_data=["Avaliação formatada", "Amostra formatada"],
    title="Avaliação média por categoria",
)
fig_avaliacao.update_traces(
    marker_color=COR_DOURADA,
    textposition="outside",
    cliponaxis=False,
    hovertemplate=(
        "<b>%{y}</b><br>Nota média: %{customdata[0]} de 5"
        "<br>Amostra: %{customdata[1]} vendas<extra></extra>"
    ),
)
fig_avaliacao.update_xaxes(range=[0, 5], title="Nota média (1–5)")
fig_avaliacao.update_yaxes(title="")
estiliza_grafico(fig_avaliacao, altura=500)
fig_avaliacao.update_layout(margin=dict(t=70, r=100, b=42, l=52))

ordem_categorias = sorted(produtos_filtrados["Categoria do Produto"].unique())
fig_precos = px.box(
    produtos_filtrados,
    x="Preço",
    y="Categoria do Produto",
    orientation="h",
    points="outliers",
    category_orders={"Categoria do Produto": ordem_categorias},
    title="Faixa de preço por categoria",
)
fig_precos.update_traces(
    line_color=COR_PRIMARIA,
    fillcolor="rgba(119, 184, 215, 0.28)",
    marker=dict(color=COR_DESTAQUE, opacity=0.48, size=4),
    hovertemplate="<b>%{y}</b><br>Preço: R$ %{x:.2f}<extra></extra>",
)
fig_precos.update_xaxes(title="Preço (R$)")
fig_precos.update_yaxes(title="")
estiliza_grafico(fig_precos, altura=450)

fig_parcelas = px.scatter(
    produtos_filtrados,
    x="Preço",
    y="Quantidade de parcelas",
    color="Categoria do Produto",
    color_discrete_sequence=PALETA_CATEGORIAS,
    hover_name="Produto",
    custom_data=["Categoria do Produto", "Vendedor"],
    render_mode="webgl",
    title="Preço × quantidade de parcelas",
)
fig_parcelas.update_traces(
    marker=dict(size=6, opacity=0.42),
    hovertemplate=(
        "<b>%{hovertext}</b><br>%{customdata[0]}"
        "<br>Preço: R$ %{x:.2f}<br>%{y:.0f} parcelas"
        "<br>Vendedor: %{customdata[1]}<extra></extra>"
    ),
)
fig_parcelas.update_xaxes(title="Preço (R$)")
fig_parcelas.update_yaxes(title="Quantidade de parcelas", dtick=1)
estiliza_grafico(fig_parcelas, altura=470)


uf_lider = receita_localizacao.loc[receita_localizacao["Receita"].idxmax()]
participacao_lider = uf_lider["Receita"] / receita_total * 100
mes_lider = vendas_mensais.loc[vendas_mensais["Receita"].idxmax()]
vendedor_lider = desempenho_vendedor.loc[desempenho_vendedor["Receita"].idxmax()]

aba_geral, aba_equipe, aba_dados = st.tabs(
    ["Visão geral", "Categorias e equipe", "Dados detalhados"]
)

with aba_geral:
    st.markdown(
        f"""
        <div class="insight-note">
            <strong>Leitura rápida.</strong>
            {html.escape(str(uf_lider["UF"]))} responde por
            {formata_decimal(participacao_lider, 1)}% da receita do recorte;
            o melhor mês foi {formata_mes(mes_lider["Data da Compra"])}, com
            {formata_moeda(mes_lider["Receita"], compacta=True)}.
        </div>
        """,
        unsafe_allow_html=True,
    )

    titulo_secao(
        "Onde a receita se concentra",
        "As bolhas usam o centro geográfico de cada UF; elas representam "
        "concentração estadual, não a localização exata de cada compra.",
    )
    col_mapa, col_estados = st.columns([1.1, 0.9], gap="medium")
    with col_mapa:
        st.plotly_chart(
            fig_mapa, width="stretch", theme="streamlit", config=CONFIG_GRAFICOS
        )
    with col_estados:
        st.plotly_chart(
            fig_estados, width="stretch", theme="streamlit", config=CONFIG_GRAFICOS
        )

    titulo_secao(
        "Como o resultado evoluiu",
        "Receita e volume aparecem em painéis alinhados para permitir "
        "comparação temporal sem misturar escalas no mesmo eixo.",
    )
    st.plotly_chart(
        fig_tendencia, width="stretch", theme="streamlit", config=CONFIG_GRAFICOS
    )

    titulo_secao(
        "Quando a receita ganha força",
        "A matriz ajuda a comparar meses entre anos. Passe o cursor para "
        "consultar o valor completo de cada período.",
    )
    st.plotly_chart(
        fig_heatmap, width="stretch", theme="streamlit", config=CONFIG_GRAFICOS
    )

with aba_equipe:
    st.markdown(
        f"""
        <div class="insight-note">
            <strong>Destaque comercial.</strong>
            {html.escape(str(vendedor_lider["Vendedor"]))} lidera o recorte com
            {formata_moeda(vendedor_lider["Receita"], compacta=True)} em receita
            e {formata_inteiro(vendedor_lider["Vendas"])} vendas.
        </div>
        """,
        unsafe_allow_html=True,
    )

    titulo_secao(
        "Quem vende e como o cliente avalia",
        "A receita mostra contribuição comercial; as notas incluem o tamanho "
        "da amostra para evitar conclusões a partir de poucos registros.",
    )
    col_vendedores, col_avaliacao = st.columns(2, gap="medium")
    with col_vendedores:
        st.plotly_chart(
            fig_vendedores,
            width="stretch",
            theme="streamlit",
            config=CONFIG_GRAFICOS,
        )
    with col_avaliacao:
        st.plotly_chart(
            fig_avaliacao,
            width="stretch",
            theme="streamlit",
            config=CONFIG_GRAFICOS,
        )

    titulo_secao(
        "Como preço e parcelamento se comportam",
        "A distribuição revela faixas e outliers; a dispersão permite observar "
        "se compras mais caras tendem a usar mais parcelas.",
    )
    st.plotly_chart(
        fig_precos, width="stretch", theme="streamlit", config=CONFIG_GRAFICOS
    )
    st.plotly_chart(
        fig_parcelas, width="stretch", theme="streamlit", config=CONFIG_GRAFICOS
    )

with aba_dados:
    titulo_secao(
        "Vendas individuais",
        "Cada linha é uma transação do recorte atual. A exportação respeita "
        "os mesmos filtros e usa separador e decimal compatíveis com Excel em pt-BR.",
    )

    detalhes_vendas = produtos_filtrados.sort_values(
        "Data da Compra", ascending=False
    ).reset_index(drop=True)
    detalhes_vendas.insert(0, "Linha", detalhes_vendas.index + 1)

    dados_exportacao = detalhes_vendas.to_csv(
        index=False, sep=";", decimal=",", date_format="%d/%m/%Y"
    ).encode("utf-8-sig")

    info_tabela, acao_exportar = st.columns(
        [3, 1], vertical_alignment="bottom", gap="medium"
    )
    with info_tabela:
        st.markdown(
            f"""
            <div class="data-note">
                <strong>{formata_inteiro(len(detalhes_vendas))} linhas</strong><br>
                <span>Ordenadas da compra mais recente para a mais antiga.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with acao_exportar:
        st.download_button(
            label="Baixar CSV",
            data=dados_exportacao,
            file_name=f"vendas_{inicio:%Y%m%d}_{fim:%Y%m%d}.csv",
            mime="text/csv",
            help="Baixa todas as linhas que correspondem ao recorte atual.",
            width="stretch",
        )

    mostrar_coordenadas = st.toggle(
        "Mostrar latitude e longitude",
        value=False,
        help="Campos técnicos usados para posicionar as UFs no mapa.",
    )
    ordem_colunas = [
        "Linha",
        "Produto",
        "Categoria do Produto",
        "Preço",
        "Frete",
        "Data da Compra",
        "Vendedor",
        "Local da compra",
        "Avaliação da compra",
        "Tipo de pagamento",
        "Quantidade de parcelas",
    ]
    if mostrar_coordenadas:
        ordem_colunas.extend(["lat", "lon"])

    st.dataframe(
        detalhes_vendas,
        column_order=ordem_colunas,
        hide_index=True,
        width="stretch",
        height=560,
        column_config={
            "Linha": st.column_config.NumberColumn("Linha", format="%d"),
            "Produto": st.column_config.TextColumn("Produto", width="large"),
            "Categoria do Produto": st.column_config.TextColumn(
                "Categoria", width="medium"
            ),
            "Preço": st.column_config.NumberColumn("Preço", format="R$ %.2f"),
            "Frete": st.column_config.NumberColumn("Frete", format="R$ %.2f"),
            "Data da Compra": st.column_config.DateColumn(
                "Data da compra", format="DD/MM/YYYY"
            ),
            "Local da compra": st.column_config.TextColumn("UF"),
            "Avaliação da compra": st.column_config.NumberColumn(
                "Avaliação", format="%d/5"
            ),
            "Quantidade de parcelas": st.column_config.NumberColumn(
                "Parcelas", format="%d"
            ),
            "lat": st.column_config.NumberColumn("Latitude", format="%.2f"),
            "lon": st.column_config.NumberColumn("Longitude", format="%.2f"),
        },
    )

st.caption(
    "Fonte: API pública LabDados. Receita corresponde à soma do preço dos "
    "produtos; o frete é apresentado separadamente."
)
