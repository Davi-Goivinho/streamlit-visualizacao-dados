from __future__ import annotations

import warnings
from typing import Any

# pyrefly: ignore [missing-import]
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler


#Features utilizadas no modelo

FEATURES_PADRAO = [
    "Preço",
    "Frete",
    "Quantidade de parcelas",
    #"Avaliação da compra",
]

# Etapa 1 — Pré-processamento


def prepara_features(
    df: pd.DataFrame,
    features: list[str] = FEATURES_PADRAO,
) -> tuple[pd.DataFrame, np.ndarray, StandardScaler]:

    df_limpo = df.dropna(subset=features).copy()
    X = df_limpo[features].values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    return df_limpo, X_scaled, scaler


# Etapa 2 — Método do Cotovelo (Elbow + Silhouette)


def calcula_elbow(
    X_scaled: np.ndarray,
    k_min: int = 2,
    k_max: int = 10,
    amostra: int | None = 5000,
) -> pd.DataFrame:

    n_amostras = X_scaled.shape[0]

    resultados = []
    for k in range(k_min, k_max + 1):
        km = KMeans(n_clusters=k, random_state=42, n_init="auto")
        rotulos = km.fit_predict(X_scaled)
        inercia = km.inertia_

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            if amostra and n_amostras > amostra:
                rng = np.random.default_rng(42)
                idx = rng.choice(n_amostras, size=amostra, replace=False)
                sil = silhouette_score(X_scaled[idx], rotulos[idx])
            else:
                sil = silhouette_score(X_scaled, rotulos)

        resultados.append({"k": k, "inercia": inercia, "silhouette": sil})

    return pd.DataFrame(resultados)


#Etapa 3 — Aplicar K-Means


def aplica_kmeans(
    df: pd.DataFrame,
    X_scaled: np.ndarray,
    n_clusters: int = 4,
) -> pd.DataFrame:

    km = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
    df = df.copy()
    df["Cluster_raw"] = km.fit_predict(X_scaled)

    # Reordena os clusters pelo ticket médio (menor → maior)
    ordem = (
        df.groupby("Cluster_raw")["Preço"]
        .mean()
        .sort_values()
        .reset_index()
    )
    mapa_ordem = {raw: idx + 1 for idx, raw in enumerate(ordem["Cluster_raw"])}

    df["Cluster"] = df["Cluster_raw"].map(mapa_ordem).astype(str)
    df["Cluster_label"] = df["Cluster"].map(lambda c: f"Grupo {c}")
    df.drop(columns=["Cluster_raw"], inplace=True)

    return df


# Etapa 4 — Resumo por cluster


def agrega_por_cluster(df: pd.DataFrame) -> pd.DataFrame:
    """
    Gera tabela-resumo com métricas agregadas de cada cluster.
    """
    resumo = (
        df.groupby("Cluster_label")
        .agg(
            Vendas=("Preço", "size"),
            Receita_Total=("Preço", "sum"),
            Ticket_Médio=("Preço", "mean"),
            Frete_Médio=("Frete", "mean"),
            Parcelas_Médias=("Quantidade de parcelas", "mean"),
            Avaliação_Média=("Avaliação da compra", "mean"),
            Estados=("Local da compra", lambda x: ", ".join(sorted(x.unique()))),
            Categorias=("Categoria do Produto", lambda x: ", ".join(
                x.value_counts().head(3).index.tolist()
            )),
        )
        .reset_index()
        .rename(columns={"Cluster_label": "Cluster"})
        .sort_values("Ticket_Médio", ascending=True)
        .round(2)
    )
    return resumo


# Pipeline completo


def pipeline_completo(
    df: pd.DataFrame,
    n_clusters: int = 4,
    features: list[str] = FEATURES_PADRAO,
    calcular_elbow: bool = True,
    k_max_elbow: int = 10,
) -> dict[str, Any]:
    """
    Executa o fluxo completo e retorna todos os artefatos.
    """
    # Passo 1: normalizar features
    df_limpo, X_scaled, scaler = prepara_features(df, features=features)
    n_transacoes = len(df_limpo)

    # Passo 2: curva do cotovelo (opcional)
    metricas_elbow = None
    if calcular_elbow:
        k_max = min(k_max_elbow, n_transacoes - 1)
        metricas_elbow = calcula_elbow(X_scaled, k_min=2, k_max=k_max)

    # Passo 3: aplicar K-Means
    df_clusterizado = aplica_kmeans(df_limpo, X_scaled, n_clusters=n_clusters)

    # Passo 4: gerar resumo
    resumo = agrega_por_cluster(df_clusterizado)

    return {
        "df_clusterizado": df_clusterizado,
        "resumo_clusters": resumo,
        "metricas_elbow": metricas_elbow,
        "n_transacoes": n_transacoes,
        "features_usadas": features,
        "n_clusters": n_clusters,
    }


# Execução direta: python analytics/clustering.py

if __name__ == "__main__":
    import requests

    SEP = "─" * 60

    print(SEP)
    print("  CLUSTERIZAÇÃO POR PERFIL DE COMPRA — LabDados")
    print(SEP)

    # Carrega dados 
    print("\n📥 Baixando dados da API...")
    response = requests.get("https://labdados.com/produtos", timeout=20)
    response.raise_for_status()

    df = pd.DataFrame(response.json())
    df["Data da Compra"] = pd.to_datetime(
        df["Data da Compra"], format="%d/%m/%Y", errors="coerce"
    )
    print(f"   {len(df):,} transações carregadas.\n")

    # Roda o pipeline 
    N_CLUSTERS = 4
    print(f"  Rodando pipeline com k={N_CLUSTERS}...")
    print(f"   Features: {', '.join(FEATURES_PADRAO)}")
    resultado = pipeline_completo(
        df,
        n_clusters=N_CLUSTERS,
        calcular_elbow=True,
        k_max_elbow=10,
    )

    # Metadados 
    print(f"\n{SEP}")
    print("  METADADOS")
    print(SEP)
    print(f"  Transações analisadas : {resultado['n_transacoes']:,}")
    print(f"  Clusters gerados      : {resultado['n_clusters']}")
    print(f"  Features usadas       : {', '.join(resultado['features_usadas'])}")

    # Elbow Method
    if resultado["metricas_elbow"] is not None:
        print(f"\n{SEP}")
        print("  ELBOW METHOD (inércia + silhouette por k)")
        print(SEP)
        elbow = resultado["metricas_elbow"]
        melhor_k = int(elbow.loc[elbow["silhouette"].idxmax(), "k"])
        print(f"  {'k':>4}  {'Inércia':>12}  {'Silhouette':>12}  {'':>6}")
        for _, linha in elbow.iterrows():
            k_val = int(linha["k"])
            marcador = " ◀ melhor" if k_val == melhor_k else ""
            print(
                f"  {k_val:>4}  {linha['inercia']:>12.2f}  "
                f"{linha['silhouette']:>12.4f}{marcador}"
            )
        print(f"\n  Melhor k pelo Silhouette: {melhor_k}")

    # Resumo por cluster 
    print(f"\n{SEP}")
    print("  PERFIL DE CADA CLUSTER")
    print(SEP)
    resumo = resultado["resumo_clusters"]
    for _, row in resumo.iterrows():
        print(f"\n   {row['Cluster']}")
        print(f"     Vendas          : {int(row['Vendas']):,}")
        print(f"     Receita total   : R$ {row['Receita_Total']:>12,.2f}")
        print(f"     Ticket médio    : R$ {row['Ticket_Médio']:>8,.2f}")
        print(f"     Frete médio     : R$ {row['Frete_Médio']:>8,.2f}")
        print(f"     Parcelas médias : {row['Parcelas_Médias']:.2f}")
        print(f"     Avaliação média : {row['Avaliação_Média']:.2f} / 5")
        print(f"     Top 3 categorias: {row['Categorias']}")
        print(f"     Estados         : {row['Estados']}")

    # Distribuição de transações por cluster
    print(f"\n{SEP}")
    print("  DISTRIBUIÇÃO")
    print(SEP)
    total = len(resultado["df_clusterizado"])
    dist = resultado["df_clusterizado"]["Cluster_label"].value_counts()
    for cluster, count in dist.items():
        pct = count / total * 100
        barra = "█" * int(pct / 2)
        print(f"  {cluster:<15} {count:>5,} ({pct:>5.1f}%)  {barra}")

    # Amostra 
    print(f"\n{SEP}")
    print("  AMOSTRA — 5 transações de cada cluster")
    print(SEP)
    colunas = ["Produto", "Preço", "Quantidade de parcelas", "Avaliação da compra",
               "Local da compra", "Cluster_label"]
    for nome_cluster in sorted(resultado["df_clusterizado"]["Cluster_label"].unique()):
        amostra = (
            resultado["df_clusterizado"]
            .query("Cluster_label == @nome_cluster")[colunas]
            .sample(n=min(3, len(resultado["df_clusterizado"]
                    .query("Cluster_label == @nome_cluster"))), random_state=42)
        )
        print(f"\n  ── {nome_cluster} ──")
        print(amostra.to_string(index=False))

    print(f"\n{SEP}")
    print("  Pipeline concluído com sucesso.")
    print(SEP)
