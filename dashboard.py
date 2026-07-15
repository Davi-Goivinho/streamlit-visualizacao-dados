# pyrefly: ignore [missing-import]
import streamlit as st
import requests
import pandas as pd
# pyrefly: ignore [missing-import]
import plotly.express as px
# pyrefly: ignore [missing-import]
import plotly.graph_objects as go
# pyrefly: ignore [missing-import]
from plotly.subplots import make_subplots

# Configuração da página
st.set_page_config(layout='wide', page_title='Dashboard de Vendas', page_icon='📊')


### Funções auxiliares ###

def formata_numero(valor, prefixo = ''):
    for unidade in ['', 'mil']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'


### Base de Dados ###

url = 'https://labdados.com/produtos'
response = requests.get(url)
produtos = pd.DataFrame.from_dict(response.json())
produtos['Data da Compra'] = pd.to_datetime(produtos['Data da Compra'], format='%d/%m/%Y')


### Interface e Filtros ###

st.header('Dashboard de Vendas')

# Linha de Filtros
col_filtros = st.columns(4)

with col_filtros[0]:
    # Filtro de Período
    min_date = produtos['Data da Compra'].min().date()
    max_date = produtos['Data da Compra'].max().date()
    periodo = st.date_input(
        "Período",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

with col_filtros[1]:
    # Filtro de Categoria
    categorias = st.multiselect(
        "Categoria do Produto",
        options=sorted(produtos['Categoria do Produto'].unique())
    )

with col_filtros[2]:
    # Filtro de UF
    ufs = st.multiselect(
        "UF",
        options=sorted(produtos['Local da compra'].unique())
    )

with col_filtros[3]:
    # Filtro de Vendedor
    vendedores = st.multiselect(
        "Vendedor",
        options=sorted(produtos['Vendedor'].unique())
    )


### Aplicar Filtros ###

produtos_filtrados = produtos.copy()

# Executa o filtro de período
if len(periodo) == 2:
    start_date, end_date = periodo
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    produtos_filtrados = produtos_filtrados[
        (produtos_filtrados['Data da Compra'] >= start_date) & 
        (produtos_filtrados['Data da Compra'] <= end_date)
    ]

# Executa o filtro de categorias
if categorias:
    produtos_filtrados = produtos_filtrados[produtos_filtrados['Categoria do Produto'].isin(categorias)]

# Executa o filtro de UF
if ufs:
    produtos_filtrados = produtos_filtrados[produtos_filtrados['Local da compra'].isin(ufs)]

# Executa o filtro de vendedor
if vendedores:
    produtos_filtrados = produtos_filtrados[produtos_filtrados['Vendedor'].isin(vendedores)]


# Validação de dados vazios
if produtos_filtrados.empty:
    st.warning("Nenhum dado encontrado para os filtros selecionados.")
else:
    ### Métricas de Destaque ###
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    
    col1.metric('Quantidade de Vendas', formata_numero(len(produtos_filtrados)), border=True)
    col2.metric('Total de Receita', formata_numero(sum(produtos_filtrados['Preço']), 'R$' ), border=True)
    col3.metric('Ticket Médio', formata_numero(sum(produtos_filtrados['Preço'])/len(produtos_filtrados) if len(produtos_filtrados) > 0 else 0, 'R$' ), border=True)
    col4.metric('Média de Frete', formata_numero(sum(produtos_filtrados['Frete'])/len(produtos_filtrados) if len(produtos_filtrados) > 0 else 0, 'R$' ), border=True)

    ### Processamento dos Gráficos ###

    # Tabelas de Receita por Local de Compra
    receita_localizacao = produtos_filtrados.groupby('Local da compra')[['Preço']].sum().reset_index()
    receita_localizacao = receita_localizacao.rename(columns={'Preço': 'Receita', 'Local da compra': 'Estado'})
    
    receita_localizacao_mapa = produtos_filtrados.groupby('Local da compra')[['Preço', 'lat', 'lon']].agg({
        'Preço': 'sum',
        'lat': 'first',
        'lon': 'first'
    }).reset_index().rename(columns={'Preço': 'Receita', 'Local da compra': 'Estado'})

    # Gráfico de Barras por Estado
    fig_receita_localizacao = px.bar(
        receita_localizacao.sort_values('Receita', ascending=False),
        x='Estado', y='Receita',
        text_auto='.2s',
        title='Receita por Estado',
        template='plotly_white',
        color_discrete_sequence=['#2E5EAA']
    )
    fig_receita_localizacao.update_layout(
        title_font_size=20,
        yaxis_title='Receita (R$)',
        xaxis_title='',
        showlegend=False,
        margin=dict(t=60, b=40, l=40, r=20),
    )

    # Mapa de Receita
    fig_mapa = px.scatter_map(
        receita_localizacao_mapa,
        lat='lat',
        lon='lon',
        size='Receita',
        zoom=3.2,
        map_style='carto-darkmatter',
        hover_name='Estado',
        hover_data={'Receita': ':.2f', 'lat': False, 'lon': False},
        title='Receita por Estado',
        color_discrete_sequence=['#00D4B2'] 
    )
    fig_mapa.update_layout(
        map=dict(
            center=dict(lat=-14.2350, lon=-51.9253)
        ),
        title_font_size=20,
        margin=dict(t=60, b=40, l=20, r=20)
    )

    # Gráfico Boxplot (Distribuição de Preço)
    fig_boxplot = px.box(
        produtos_filtrados,
        x='Categoria do Produto',
        y='Preço',
        title='Distribuição de Preço por Categoria',
        template='plotly_white',
        color='Categoria do Produto',
        color_discrete_sequence=px.colors.qualitative.Prism
    )
    fig_boxplot.update_layout(
        title_font_size=20,
        yaxis_title='Preço (R$)',
        xaxis_title='',
        showlegend=False,
        margin=dict(t=60, b=40, l=40, r=20),
    )

    # Tabelas de Performance por Vendedor
    desempenho_vendedor = produtos_filtrados.groupby('Vendedor')[['Preço']].agg({'Preço': ['sum', 'count']}).reset_index()
    desempenho_vendedor.columns = ['Vendedor', 'Receita Total', 'Quantidade de Vendas']

    # Gráfico de Desempenho por Vendedor
    fig_vendedor = px.bar(
        desempenho_vendedor.sort_values('Receita Total', ascending=True),
        x='Receita Total',
        y='Vendedor',
        orientation='h',
        text_auto='.2s',
        title='Performance por Vendedor (Receita)',
        template='plotly_white',
        color='Receita Total',
        color_continuous_scale='Blues',
        hover_data={'Quantidade de Vendas': True}
    )
    fig_vendedor.update_layout(
        title_font_size=20,
        xaxis_title='Receita Total (R$)',
        yaxis_title='',
        margin=dict(t=60, b=40, l=40, r=20),
    )

    # Gráfico de Tendência de Vendas (Mensal)
    df_trend = produtos_filtrados.groupby(produtos_filtrados['Data da Compra'].dt.to_period('M')).agg(
        Receita=('Preço', 'sum'),
        Quantidade=('Preço', 'count')
    ).reset_index()
    df_trend['Data da Compra'] = df_trend['Data da Compra'].dt.to_timestamp()

    fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig_trend.add_trace(
        go.Scatter(
            x=df_trend['Data da Compra'],
            y=df_trend['Receita'],
            name="Receita (R$)",
            mode='lines+markers',
            line=dict(color='#2E5EAA', width=3),
            marker=dict(size=6)
        ),
        secondary_y=False,
    )
    fig_trend.add_trace(
        go.Scatter(
            x=df_trend['Data da Compra'],
            y=df_trend['Quantidade'],
            name="Quantidade de Peças",
            mode='lines+markers',
            line=dict(color='#F46036', width=3),
            marker=dict(size=6)
        ),
        secondary_y=True,
    )
    fig_trend.update_layout(
        title='Tendência de Vendas (Mensal)',
        title_font_size=20,
        template='plotly_white',
        hovermode='x unified',
        margin=dict(t=60, b=40, l=40, r=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig_trend.update_yaxes(title_text="Receita (R$)", secondary_y=False, gridcolor='rgba(0,0,0,0.05)')
    fig_trend.update_yaxes(title_text="Quantidade de Peças", secondary_y=True)
    fig_trend.update_xaxes(title_text="")


    # Gráfico de avaliação vendedor
    avaliacao_vendedor = produtos_filtrados.groupby('Vendedor')[['Avaliação da compra']].agg({'Avaliação da compra': 'mean'}).reset_index()
    avaliacao_vendedor = avaliacao_vendedor.rename(columns={'Avaliação da compra': 'Avaliação Média'})

    fig_avaliacao = px.bar(
        avaliacao_vendedor.sort_values('Avaliação Média', ascending=True),
        x='Avaliação Média',
        y='Vendedor',
        orientation='h',
        text_auto='.2s',
        title='Avaliação Média por Vendedor',
        template='plotly_white',
        color='Avaliação Média',
        color_continuous_scale='Blues'
    )
    fig_avaliacao.update_layout(
        title_font_size=20,
        xaxis_title='Avaliação Média (R$)',
        yaxis_title='',
        margin=dict(t=60, b=40, l=40, r=20),
    )


    ### Renderização dos Gráficos na Tela ###

    col5, col6 = st.columns(2)
    col5.plotly_chart(fig_mapa, use_container_width=True)
    col6.plotly_chart(fig_receita_localizacao, use_container_width=True)

    st.plotly_chart(fig_trend, use_container_width=True)

    col7, col8 = st.columns(2)
    col7.plotly_chart(fig_avaliacao, use_container_width=True)
    col8.plotly_chart(fig_vendedor, use_container_width=True)

    st.dataframe(produtos_filtrados, use_container_width=True)
    st.plotly_chart(fig_boxplot, use_container_width=True)