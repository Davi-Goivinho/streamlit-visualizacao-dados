import streamlit as st
import requests
import pandas as pd
import plotly.express as px


### Funções auxiliares ###

def formata_numero(valor, prefixo = ''):
    for unidade in ['', 'mil']:
        if valor <1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'


### Base de Dados ###


url = 'https://labdados.com/produtos'

response = requests.get(url)

produtos = pd.DataFrame.from_dict(response.json())


### Graficos ###

# Tabelas de Receita por Local de Compra
receita_localizacao = produtos.groupby('Local da compra')[['Preço']].sum().reset_index()
receita_localizacao = receita_localizacao.rename(columns={'Preço': 'Receita', 'Local da compra': 'Estado'})
receita_localizacao_mapa = produtos.groupby('Local da compra')[['Preço', 'lat', 'lon']].agg({
    'Preço': 'sum',
    'lat': 'first',
    'lon': 'first'
}).reset_index().rename(columns={'Preço': 'Receita', 'Local da compra': 'Estado'})

# Gráfico de Barras
fig_receita_localizacao = px.bar(
    receita_localizacao.sort_values('Receita', ascending=False),
    x='Estado', y='Receita',
    text_auto='.2s',
    title='Receita por Estado',
    template='plotly_white',
    color_discrete_sequence=['#2E5EAA']  # cor sólida, sem legenda de escala
)

fig_receita_localizacao.update_layout(
    title_font_size=20,
    yaxis_title='Receita (R$)',
    xaxis_title='',
    showlegend=False,
    margin=dict(t=60, b=40, l=40, r=20),
)

# Mapa de Receita
fig_mapa = px.scatter_geo(
    receita_localizacao_mapa,
    lat='lat',
    lon='lon',
    scope='south america',
    size='Receita',
    template='plotly_white',
    hover_name='Estado',
    hover_data={'Receita': ':.2f', 'lat': False, 'lon': False},
    title='Receita por Estado'
)


### Métricas de Destaque ###

st.set_page_config(layout='wide', page_title='Dashboard de Vendas', page_icon='📊')

st.header('Dashboard de Vendas')

col1, col2 = st.columns(2)
col3, col4 = st.columns(2)
col1.metric('Quantidade de Vendas', formata_numero(len(produtos)), border=True)
col2.metric('Total de Receita', formata_numero(sum(produtos['Preço']), 'R$' ), border=True)
col3.metric('Ticket Médio', formata_numero(sum(produtos['Preço'])/len(produtos), 'R$' ), border=True)
col4.metric('Média de Frete', formata_numero(sum(produtos['Frete'])/len(produtos), 'R$' ), border=True)

# Layout com Abas
aba1, aba2, aba3 = st.tabs(['Visualização em Mapa', 'Visualização em Gráfico', 'Tabela de Dados'])
st.dataframe(produtos)
with aba1:
    st.plotly_chart(fig_mapa, use_container_width=True)
with aba2:
    st.plotly_chart(fig_receita_localizacao, use_container_width=True)
with aba3:
    st.dataframe(produtos)