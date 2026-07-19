"""
analytics/clustering_kproto.py
==============================
Clusterização avançada de dados mistos (numéricos + categóricos)
utilizando o algoritmo K-Prototypes.

DIFERENCIAL TÉCNICO
-------------------
Ao contrário do K-Means (que exige apenas dados numéricos), o K-Prototypes
consegue lidar nativamente com colunas de texto sem a necessidade de aplicar
One-Hot Encoding (que inflaria a dimensionalidade dos dados).

Ele combina:
1. Distância Euclidiana para features numéricas (K-Means).
2. Dissimilaridade por correspondência para features categóricas (K-Modes).

COMO EXECUTAR
-------------
    python analytics/clustering_kproto.py
"""

from __future__ import annotations

import warnings
import pandas as pd
import requests
from sklearn.preprocessing import StandardScaler

# pyrefly: ignore [missing-import]
from kmodes.kprototypes import KPrototypes

# Configuração das variáveis 

FEATURES_NUMERICAS = [
    "Preço",
    "Frete",
    "Quantidade de parcelas",
    "Avaliação da compra",
]

FEATURES_CATEGORICAS = [
    "Categoria do Produto",
    "Tipo de pagamento",
]

FEATURES_TUDO = FEATURES_NUMERICAS + FEATURES_CATEGORICAS

CATEGORIAS_MAP = {
    "brinquedos": "Brinquedos",
    "eletrodomesticos": "Eletrodomésticos",
    "eletronicos": "Eletrônicos",
    "esporte e lazer": "Esporte e lazer",
    "instrumentos musicais": "Instrumentos musicais",
    "livros": "Livros",
    "moveis": "Móveis",
    "utilidades domesticas": "Utilidades domésticas",
}

PAGAMENTOS_MAP = {
    "boleto": "Boleto",
    "cartao_credito": "Cartão de crédito",
    "cartao_debito": "Cartão de débito",
    "cupom": "Cupom",
}


def prepara_dados(df: pd.DataFrame) -> tuple[pd.DataFrame, list[int]]:
    """
    Limpa os valores nulos, padroniza categorias e retorna os dados prontos.
    Retorna também a lista de índices correspondentes às colunas categóricas.
    """
    df = df.copy()

    # Tradução das categorias e pagamentos para exibição amigável
    df["Categoria do Produto"] = (
        df["Categoria do Produto"]
        .map(CATEGORIAS_MAP)
        .fillna(df["Categoria do Produto"].str.capitalize())
    )
    df["Tipo de pagamento"] = (
        df["Tipo de pagamento"]
        .map(PAGAMENTOS_MAP)
        .fillna(df["Tipo de pagamento"].str.replace("_", " ").str.capitalize())
    )

    # Remove nulos das colunas que usaremos
    df_limpo = df.dropna(subset=FEATURES_TUDO).copy()

    # O K-Prototypes trabalha com uma matriz onde as colunas categóricas precisam
    # estar bem mapeadas por índice.
    # Vamos criar a estrutura final de colunas: numéricas primeiro, depois categóricas.
    df_modelo = df_limpo[FEATURES_TUDO].copy()

    # Normaliza APENAS as colunas numéricas
    scaler = StandardScaler()
    df_modelo[FEATURES_NUMERICAS] = scaler.fit_transform(
        df_modelo[FEATURES_NUMERICAS]
    )

    # Identifica os índices numéricos das colunas categóricas
    # Ex: se FEATURES_TUDO tem 4 numéricas e 2 categóricas, os índices categóricos serão [4, 5]
    indices_categoricos = [
        df_modelo.columns.get_loc(col) for col in FEATURES_CATEGORICAS
    ]

    # Retornamos o dataframe com os valores originais nas categóricas e normalizados nas numéricas,
    # além do dataframe original limpo para podermos fazer o agrupamento final sem normalização.
    return df_modelo, indices_categoricos, df_limpo


def executa_kprototypes(df_orig: pd.DataFrame, n_clusters: int = 4) -> pd.DataFrame:
    """Runs K-Prototypes and merges cluster labels back to the original df."""
    df_modelo, indices_categoricos, df_limpo = prepara_dados(df_orig)

    print(f"⚙️  Treinando K-Prototypes com k={n_clusters}...")
    print(f"   Numerical features: {FEATURES_NUMERICAS}")
    print(f"   Categorical features: {FEATURES_CATEGORICAS}")

    # Inicializa o K-Prototypes
    # O método 'Cao' é recomendado para inicialização inteligente de dados categóricos.
    kproto = KPrototypes(
        n_clusters=n_clusters, init="Cao", random_state=42, n_init=3
    )

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        # Treina e prediz os clusters
        clusters = kproto.fit_predict(
            df_modelo.values, categorical=indices_categoricos
        )

    # Adiciona as labels de volta no dataframe limpo (com valores originais para análise)
    df_limpo["Cluster"] = (clusters + 1).astype(str)
    df_limpo["Cluster_label"] = df_limpo["Cluster"].map(lambda c: f"Grupo {c}")

    return df_limpo


def analisa_resumo(df_final: pd.DataFrame) -> pd.DataFrame:
    """Gera o perfil descritivo de cada cluster gerado pelo K-Prototypes."""
    resumo = (
        df_final.groupby("Cluster_label")
        .agg(
            Vendas=("Preço", "size"),
            Receita_Total=("Preço", "sum"),
            Ticket_Médio=("Preço", "mean"),
            Frete_Médio=("Frete", "mean"),
            Parcelas_Médias=("Quantidade de parcelas", "mean"),
            Avaliação_Média=("Avaliação da compra", "mean"),
            Moda_Categoria=("Categoria do Produto", lambda x: x.mode()[0]),
            Moda_Pagamento=("Tipo de pagamento", lambda x: x.mode()[0]),
            Top_Estados=("Local da compra", lambda x: ", ".join(
                x.value_counts().head(3).index.tolist()
            )),
        )
        .reset_index()
        .rename(columns={"Cluster_label": "Cluster"})
        .sort_values("Ticket_Médio", ascending=True)
        .round(2)
    )
    return resumo


# Execução direta no terminal

if __name__ == "__main__":
    import numpy as np

    SEP = "─" * 70

    print(SEP)
    print("  CLUSTERIZAÇÃO DE DADOS MISTOS (K-PROTOTYPES) — LabDados")
    print(SEP)

    # 1. Carrega dados
    print("\n📥 Baixando dados da API...")
    try:
        response = requests.get("https://labdados.com/produtos", timeout=20)
        response.raise_for_status()
        df = pd.DataFrame(response.json())
        print(f"   {len(df):,} transações carregadas com sucesso.")
    except Exception as e:
        print(f"❌ Erro ao baixar dados: {e}")
        exit(1)

    # 2. Executa algoritmo
    df_com_clusters = executa_kprototypes(df, n_clusters=4)

    # 3. Gera resumo descritivo
    resumo = analisa_resumo(df_com_clusters)

    # 4. Printa Metadados
    print(f"\n{SEP}")
    print("  METADADOS DOS GRUPOS")
    print(SEP)
    total_linhas = len(df_com_clusters)
    dist = df_com_clusters["Cluster_label"].value_counts()

    for idx, row in resumo.iterrows():
        n_vendas = row["Vendas"]
        pct = (n_vendas / total_linhas) * 100
        barra = "█" * int(pct / 2)

        print(f"\n  📦 {row['Cluster']} ({pct:.1f}% das vendas)  {barra}")
        print(f"     Quantidade de Vendas : {n_vendas:,}")
        print(f"     Receita Total        : R$ {row['Receita_Total']:,.2f}")
        print(f"     Ticket Médio         : R$ {row['Ticket_Médio']:,.2f}")
        print(f"     Frete Médio          : R$ {row['Frete_Médio']:,.2f}")
        print(f"     Parcelas Médias      : {row['Parcelas_Médias']:.1f}")
        print(f"     Avaliação Média      : {row['Avaliação_Média']:.2f} / 5")
        print(f"     Categoria Mais Comum : {row['Moda_Categoria']}")
        print(f"     Pagamento Mais Comum : {row['Moda_Pagamento']}")
        print(f"     Principais Estados   : {row['Top_Estados']}")

    print(f"\n{SEP}")
    print("  ✅ Análise avançada com K-Prototypes concluída!")
    print(SEP)
