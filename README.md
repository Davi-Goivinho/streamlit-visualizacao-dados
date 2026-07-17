# 📊 Dashboard de Vendas — Análise Interativa com Streamlit

> Dashboard interativo construído em Python com Streamlit e Plotly para análise exploratória de dados de vendas e-commerce, incluindo um módulo de clusterização geográfica com K-Means (scikit-learn).  
> Projeto desenvolvido como parte do portfólio de Análise de Dados e Ciência de Dados.

---

## 🚀 Tecnologias

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python_3.14-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-239120?style=for-the-badge&logo=plotly&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas_3.0-150458?style=for-the-badge&logo=pandas&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)

---

## 📋 Sobre o Projeto

Este dashboard permite explorar dados de vendas de um e-commerce brasileiro de forma visual e interativa. O usuário pode filtrar os dados por período, categoria de produto, UF e vendedor — e todos os gráficos e métricas são atualizados em tempo real.

Os dados são consumidos diretamente de uma API pública (`labdados.com/produtos`) e abrangem **9.435 registros** de vendas entre **2020 e 2023**, distribuídos por **27 estados brasileiros**.

O projeto inclui também um **módulo de Machine Learning** (`analytics/`) que identifica mercados regionais por coordenadas geográficas e aplica K-Means para segmentá-los por perfil de compra.

---

## ✨ Funcionalidades

### 🎛️ Filtros Dinâmicos

| Filtro | Tipo | Descrição |
|--------|------|-----------|
| **Período** | Date Range | Intervalo de datas de compra |
| **Categoria do Produto** | Multiselect | Livros, Eletrônicos, Móveis, etc. |
| **UF** | Multiselect | Estado de origem da compra |
| **Vendedor** | Multiselect | Seleção individual por vendedor |

> Filtros ativos são refletidos em todos os gráficos, métricas, tabela e exportação CSV simultaneamente.

### 📈 Visualizações (3 abas)

**Visão geral**

| Gráfico | Tipo | Objetivo |
|---------|------|----------|
| Distribuição geográfica da receita | Scatter Map (tema claro/escuro) | Concentração estadual das vendas |
| 10 estados com maior receita | Barras Horizontais | Ranking dos estados por faturamento |
| Receita e volume por mês | Linhas + Barras (eixo duplo) | Tendência mensal de receita e quantidade |
| Sazonalidade da receita | Heatmap Mês × Ano | Identificar meses fortes e fracos entre anos |

**Categorias e equipe**

| Gráfico | Tipo | Objetivo |
|---------|------|----------|
| Receita por vendedor | Barras Horizontais | Performance comercial individual |
| Avaliação média por categoria | Barras Horizontais | Satisfação por linha de produto (nota + amostra) |
| Faixa de preço por categoria | Boxplot Horizontal | Dispersão, mediana e outliers de preço |
| Preço × quantidade de parcelas | Scatter Plot (WebGL) | Correlação entre ticket e parcelamento |

**Dados detalhados**

| Recurso | Descrição |
|---------|-----------|
| Tabela de vendas individuais | Todas as transações do recorte, ordenadas da mais recente |
| Exportação CSV | Download com separador `;` e decimal `,` (Excel pt-BR) |
| Toggle de coordenadas | Exibe/oculta lat/lon na tabela |

### 🧮 Métricas (KPI Strip)

- **Vendas** — Quantidade de transações no recorte
- **Receita** — Faturamento acumulado (com formatação compacta)
- **Ticket médio** — Preço médio por transação
- **Frete médio** — Custo logístico médio

### 💡 Insights Automáticos

O dashboard gera automaticamente notas de leitura rápida com base nos dados filtrados, como o estado líder em receita, o melhor mês e o vendedor destaque.

---

## 🤖 Módulo de Clusterização (Machine Learning)

O módulo `analytics/clustering.py` é independente do dashboard e pode ser executado no terminal ou importado em notebooks.

### Premissa

O dataset não possui um ID de cliente. A estratégia adotada é inferir um identificador regional: cada par único de `(lat, lon)` é tratado como um **mercado regional**. Como as coordenadas representam o centróide de cada UF, o resultado é uma segmentação estadual por perfil de compra.

### Pipeline

```
Dados brutos → Identificação de mercados (lat/lon)
             → Agregação de perfil (ticket, frete, parcelas)
             → Normalização (StandardScaler)
             → Método do Cotovelo (Elbow + Silhouette)
             → K-Means (n clusters configurável)
             → Propagação para transações originais
             → Resumo por cluster
```

### Features utilizadas

| Feature | Tipo | Descrição |
|---------|------|-----------|
| `lat`, `lon` | Geográfica | Localização do mercado |
| `Preço` | Comportamental | Ticket médio do mercado |
| `Frete` | Comportamental | Frete médio |
| `Quantidade de parcelas` | Comportamental | Média de parcelas |

### Resultado de exemplo (k=4)

| Cluster | Vendas | Receita | Ticket Médio | Regiões |
|---------|--------|---------|--------------|---------|
| Grupo A | 8.371 | R$ 5,2 mi | R$ 624 | SP, RJ, MG, PR, RS, SC, ES |
| Grupo D | 1.026 | R$ 612 mil | R$ 597 | BA, CE, PE, MA + 7 UFs |
| Grupo C | 36 | R$ 27 mil | R$ 752 | AC, AM, RO |
| Grupo B | 2 | R$ 4 mil | R$ 2.098 | RR |

### Como executar

```bash
# A partir da raiz do projeto:
python analytics/clustering.py
```

O output formatado no terminal inclui: metadados, tabela do Elbow Method com indicação do melhor k, resumo por cluster e amostra de transações clusterizadas.

---

## 🗂️ Estrutura do Projeto

```
streamlit-visualizacao-dados/
│
├── dashboard.py                 # Aplicação principal (Streamlit)
├── requirements.txt             # Dependências do projeto
├── README.md                    # Documentação
│
├── assets/
│   └── styles.css               # CSS customizado (separado do Python)
│
├── analytics/
│   ├── __init__.py              # Torna a pasta um módulo Python
│   └── clustering.py            # Pipeline de clusterização K-Means
│
├── .streamlit/
│   └── config.toml              # Tema claro/escuro customizado
│
└── .devcontainer/
    └── devcontainer.json        # Configuração para GitHub Codespaces
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
| **scikit-learn** | 1.9.0 | Clusterização K-Means e métricas |

---

## ⚙️ Como Executar Localmente

### Pré-requisitos
- Python 3.10+
- Git

### Passo a Passo

```bash
# 1. Clone o repositório
git clone https://github.com/Davi-Goivinho/streamlit-visualizacao-dados.git
cd streamlit-visualizacao-dados

# 2. Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate      # Linux/macOS
.venv\Scripts\activate       # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Execute o dashboard
streamlit run dashboard.py

# 5. (Opcional) Execute a análise de clusterização no terminal
python analytics/clustering.py
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

### Dashboard
- **Filtragem reativa** — todos os gráficos e métricas respondem em tempo real com `st.session_state`
- **Cache de dados** — `st.cache_data(ttl=3600)` evita chamadas desnecessárias à API
- **Tema dinâmico** — alternância automática claro/escuro via `st.context.theme`
- **CSS modular** — estilos extraídos para arquivo externo (`assets/styles.css`)
- **Agrupamento e agregação** com Pandas (`groupby`, `agg`, `pivot`)
- **Séries temporais** — decomposição por período (`.dt.to_period('M')`)
- **Visualização geoespacial** — mapa interativo com Plotly MapLibre
- **Gráficos de eixo duplo** — `make_subplots` com linhas + barras
- **Heatmap matricial** — tabela pivô Mês × Ano com anotações formatadas
- **HTML semântico** — KPIs com `<dl>`, `<dt>`, `<dd>` para acessibilidade
- **Consumo de API REST** com `requests` e validação de colunas obrigatórias
- **Exportação CSV** — separador `;`, decimal `,` e encoding `utf-8-sig` (Excel pt-BR)

### Machine Learning (módulo `analytics/`)
- **Engenharia de features** — inferência de ID de cliente por coordenadas geográficas
- **Pré-processamento** — normalização com `StandardScaler` (Z-score)
- **Elbow Method** — curva de inércia (WCSS) + Silhouette Score para escolha de k
- **K-Means** — segmentação não-supervisionada de mercados regionais
- **Arquitetura modular** — separação de responsabilidades (UI × ML)

---

## 📌 Próximos Passos

- [ ] Integrar a clusterização K-Means no dashboard (nova aba com mapa colorido por cluster e tabela de perfil)
- [ ] Adicionar slider interativo para alterar o número de clusters (k) em tempo real
- [ ] Exibir curva do cotovelo (Elbow Method) no dashboard para justificar a escolha de k
- [ ] Análise de Cohort por período de primeira compra
- [ ] Previsão de vendas futuras com Prophet / statsmodels
- [ ] Predição de avaliação da compra com Random Forest
- [ ] Detecção de anomalias em transações (Isolation Forest)
- [ ] Deploy na Streamlit Community Cloud

---

## 📄 Licença

Este projeto está sob a licença MIT. Sinta-se à vontade para usar, modificar e distribuir.
