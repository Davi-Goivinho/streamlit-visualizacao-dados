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

O projeto conta com dois scripts no diretório `analytics/` que abordam a segmentação de compradores sob óticas diferentes: o **K-Means clássico** e o **K-Prototypes avançado** (para dados mistos). Ambos rodam de forma independente do dashboard.

---

### Abordagem 1: K-Means (Perfil de Compra Numérico)
Trata cada transação como um cliente individual e agrupa os compradores exclusivamente por suas variáveis comportamentais numéricas.

* **Arquivo:** `analytics/clustering.py`
* **Features:** `Preço`, `Frete`, `Quantidade de parcelas`, `Avaliação da compra`
* **Limitação:** Não consegue usar variáveis descritivas (texto) como categoria do produto e tipo de pagamento sem inflar a dimensionalidade (One-Hot Encoding).

#### Resultado (k=4) no K-Means
| Cluster | Vendas | % Total | Ticket Médio | Parcelas | Perfil do Cluster |
|---------|--------|---------|--------------|----------|-------------------|
| **Grupo 1 (Econômico)** | 5.477 | 58,0% | R$ 203 | 1,8 | Compras baratas, à vista, frete baixo, alta satisfação |
| **Grupo 2 (Intermediário)** | 1.477 | 15,7% | R$ 378 | 8,1 | Ticket baixo, parcelamento alto — comprador a crédito |
| **Grupo 3 (Premium)** | 1.650 | 17,5% | R$ 1.227 | 1,9 | Compras caras, pagamento à vista |
| **Grupo 4 (Alto Valor)** | 831 | 8,8% | R$ 2.611 | 3,2 | Ticket altíssimo — eletrônicos e eletrodomésticos |

---

### Abordagem 2: K-Prototypes (Discussão Avançada de Dados Mistos)
Para demonstrar um maior domínio conceitual e de arquitetura de dados, foi implementado o **K-Prototypes** (usando a biblioteca `kmodes`). Ele resolve o limite do K-Means permitindo calcular distâncias em dados mistos.

* **Arquivo:** `analytics/clustering_kproto.py`
* **Features Numéricas:** `Preço`, `Frete`, `Quantidade de parcelas`, `Avaliação da compra`
* **Features Categóricas:** `Categoria do Produto`, `Tipo de pagamento`

#### Diferencial Técnico do K-Prototypes
Em vez de forçar o mapeamento de palavras em números artificiais (Label Encoding) ou criar 10 colunas extras de 0 e 1 (One-Hot Encoding), o K-Prototypes aplica **Distância Euclidiana** para as variáveis numéricas e a **dissimilaridade por correspondência** para as categóricas (usando a moda como centróide do grupo de texto).

#### Resultado Prático (k=4) no K-Prototypes
O algoritmo revelou grupos muito mais profundos sobre a base de vendas:
* **Grupo 1 (Detratores / Insatisfeitos - 18,7%):** Clientes com ticket de R$ 337 e **pior avaliação média (1,77 / 5)**. Focado em Móveis.
* **Grupo 2 (Compradores de Tecnologia - 15,4%):** Ticket altíssimo de R$ 2.191 com frete de R$ 116. Focado em **Eletrônicos** no cartão.
* **Grupo 3 (Promotores Móveis - 52,8%):** O maior grupo da base. Ticket de R$ 323, pagamento à vista, **excelente satisfação (4,75 / 5)**.
* **Grupo 4 (Parcelados em Móveis - 13,2%):** Ticket de R$ 393 com **média de parcelas de 8,5**.

> 💡 **Nota de Estudo:** Enquanto o K-Means clássico segmentou apenas por faixa de preço, o K-Prototypes isolou de forma brilhante o perfil de satisfação (promotores vs detratores) e a categoria mais comprada.

---

### Como executar as análises localmente

A partir da raiz do projeto:

```bash
# Executa o modelo K-Means com avaliação do Silhouette
python analytics/clustering.py

# Executa o modelo avançado K-Prototypes para dados mistos
python analytics/clustering_kproto.py
```


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
- **Clusterização comportamental** — cada transação é tratada como um cliente individual, agrupada por perfil de compra
- **Pré-processamento** — normalização com `StandardScaler` (Z-score) para equilibrar escalas
- **Elbow Method** — curva de inércia (WCSS) + Silhouette Score para escolha do melhor k
- **K-Means** — segmentação não-supervisionada com rótulos ordenados por ticket médio
- **Arquitetura modular** — separação de responsabilidades (UI × ML), executável standalone

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
