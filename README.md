# 📊 Dashboard de Vendas — Análise Interativa com Streamlit

> Dashboard interativo construído em Python com Streamlit e Plotly para análise exploratória de dados de vendas e-commerce.  
> Projeto desenvolvido como parte do portfólio de Análise de Dados e Ciência de Dados.

---

## 🚀 Demonstração

![Dashboard Preview](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python_3.14-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-239120?style=for-the-badge&logo=plotly&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas_3.0-150458?style=for-the-badge&logo=pandas&logoColor=white)

---

## 📋 Sobre o Projeto

Este dashboard permite explorar dados de vendas de um e-commerce brasileiro de forma visual e interativa. O usuário pode filtrar os dados por período, categoria de produto, UF e vendedor — e todos os gráficos e métricas são atualizados em tempo real.

Os dados são consumidos diretamente de uma API pública (`labdados.com/produtos`) e abrangem **9.435 registros** de vendas entre **2020 e 2023**, distribuídos por **27 estados brasileiros**.

---

## ✨ Funcionalidades

### 🎛️ Filtros Dinâmicos (Barra Superior)
| Filtro | Tipo | Descrição |
|--------|------|-----------|
| **Período** | Date Range | Intervalo de datas de compra |
| **Categoria do Produto** | Multiselect | Livros, Eletrônicos, Móveis, etc. |
| **UF** | Multiselect | Estado de origem da compra |
| **Vendedor** | Multiselect | Seleção individual por vendedor |

### 📈 Visualizações

| Gráfico | Tipo | Objetivo |
|---------|------|----------|
| **Mapa de Receita por Estado** | Scatter Map (Tema Escuro) | Distribuição geográfica das vendas no Brasil |
| **Receita por Estado** | Barras Verticais | Ranking dos estados por faturamento |
| **Tendência de Vendas** | Linhas (Eixo Duplo) | Evolução mensal de receita e volume de peças |
| **Heatmap Receita Mensal** | Imshow / Heatmap | Sazonalidade de receita por Mês × Ano |
| **Distribuição de Preço** | Boxplot | Variação e outliers de preço por categoria |
| **Performance por Vendedor** | Barras Horizontais | Ranking de receita total por vendedor |
| **Avaliação por Categoria** | Barras Horizontais | Nota média de satisfação por categoria |
| **Preço × Parcelas** | Scatter Plot | Correlação entre ticket e parcelamento |

### 🧮 Métricas Principais
- **Quantidade de Vendas** — Volume total de transações no período
- **Total de Receita** — Faturamento acumulado
- **Ticket Médio** — Preço médio por transação
- **Média de Frete** — Custo logístico médio

---

## 🗂️ Estrutura do Projeto

```
streamlit-visualizacao-dados/
│
├── dashboard.py        # Código principal do dashboard
├── README.md           # Documentação do projeto
└── .venv/              # Ambiente virtual Python
```

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Versão | Uso |
|---|---|---|
| **Python** | 3.14 | Linguagem principal |
| **Streamlit** | 1.59.2 | Framework do dashboard web |
| **Plotly** | 6.9.0 | Gráficos interativos e mapas |
| **Pandas** | 3.0.3 | Manipulação e análise dos dados |
| **Requests** | 2.34.2 | Consumo da API de dados |

---

## ⚙️ Como Executar Localmente

### Pré-requisitos
- Python 3.10+
- Git

### Passo a Passo

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/streamlit-visualizacao-dados.git
cd streamlit-visualizacao-dados

# 2. Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate      # Linux/macOS
# .venv\Scripts\activate       # Windows

# 3. Instale as dependências
pip install streamlit plotly pandas requests

# 4. Execute o dashboard
streamlit run dashboard.py
```

O dashboard estará disponível em **http://localhost:8501** no seu navegador.

---

## 📊 Fonte dos Dados

Os dados são obtidos via requisição HTTP à API pública:

```
GET https://labdados.com/produtos
```

**Colunas disponíveis:**

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `Produto` | String | Nome do produto |
| `Categoria do Produto` | String | Categoria (livros, eletrônicos, etc.) |
| `Preço` | Float | Valor do produto (R$) |
| `Frete` | Float | Custo do frete (R$) |
| `Data da Compra` | Date | Data da transação (DD/MM/AAAA) |
| `Vendedor` | String | Nome do vendedor |
| `Local da compra` | String | UF de origem |
| `Avaliação da compra` | Int | Nota do cliente (1–5 estrelas) |
| `Tipo de pagamento` | String | Crédito, débito, boleto ou cupom |
| `Quantidade de parcelas` | Int | Número de parcelas (1–24) |
| `lat` / `lon` | Float | Coordenadas geográficas do estado |

---

## 🧠 Conceitos e Técnicas Aplicadas

- **Filtragem reativa** — todos os gráficos respondem em tempo real aos filtros sem necessidade de recarregar a página
- **Agrupamento e agregação** com Pandas (`groupby`, `agg`, `pivot`)
- **Séries temporais** — decomposição por período (`.dt.to_period('M')`)
- **Visualização geoespacial** — mapa interativo com Plotly MapLibre + tema escuro CartoDB
- **Gráficos de eixo duplo** — comparando métricas de escalas diferentes (receita × quantidade)
- **Heatmap matricial** — criação de tabela pivô Mês × Ano para identificar sazonalidade
- **Consumo de API REST** com `requests` e tratamento de dados com `pandas`

---

## 📌 Próximos Passos

- [ ] Análise de Cohort por período de compra
- [ ] Segmentação de clientes com K-Means (Machine Learning)
- [ ] Previsão de vendas futuras com Prophet
- [ ] Predição de avaliação da compra com Random Forest



---

## 📄 Licença

Este projeto está sob a licença MIT. Sinta-se à vontade para usar, modificar e distribuir.
