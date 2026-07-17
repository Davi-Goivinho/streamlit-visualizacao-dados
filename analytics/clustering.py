

from __future__ import annotations

import warnings
from typing import Any

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

# ---------------------------------------------------------------------------
# Configuração das features utilizadas no modelo
# ---------------------------------------------------------------------------

FEATURES_GEO = ["lat", "lon"]

FEATURES_COMPORTAMENTO = ["Preço", "Frete", "Quantidade de parcelas"]

FEATURES_PADRAO = FEATURES_GEO + FEATURES_COMPORTAMENTO

ROTULOS_CLUSTER = {
    "0": "Grupo A",
    "1": "Grupo B",
    "2": "Grupo C",
    "3": "Grupo D",
    "4": "Grupo E",
    "5": "Grupo F",
    "6": "Grupo G",
    "7": "Grupo H",
}


# ---------------------------------------------------------------------------
# Etapa 1 — Identificação do cliente por lat/lon
# ---------------------------------------------------------------------------


def cria_id_cliente(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()
    df["lat_round"] = df["lat"].round(2)
    df["lon_round"] = df["lon"].round(2)
    df["id_cliente"] = (
        df["lat_round"].astype(str) + "_" + df["lon_round"].astype(str)
    )
    return df


def resume_por_cliente(df: pd.DataFrame) -> pd.DataFrame:

    perfil = (
        df.groupby("id_cliente")
        .agg(
            lat=("lat", "first"),
            lon=("lon", "first"),
            local=("Local da compra", "first"),
            Preço=("Preço", "mean"),
            Frete=("Frete", "mean"),
            **{"Quantidade de parcelas": ("Quantidade de parcelas", "mean")},
            total_vendas=("Preço", "size"),
            receita_total=("Preço", "sum"),
            avaliacao_media=("Avaliação da compra", "mean"),
        )
        .reset_index()
    )
    return perfil


# ---------------------------------------------------------------------------
# Etapa 2 — Pré-processamento e escalonamento
# ---------------------------------------------------------------------------


def prepara_features(
    perfil: pd.DataFrame,
    features: list[str] = FEATURES_PADRAO,
) -> tuple[np.ndarray, StandardScaler]:

    X = perfil[features].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    return X_scaled, scaler


# ---------------------------------------------------------------------------
# Etapa 3 — Escolha do número ideal de clusters (Método do Cotovelo)
# ---------------------------------------------------------------------------


def calcula_elbow(
    X_scaled: np.ndarray,
    k_min: int = 2,
    k_max: int = 10,
) -> pd.DataFrame:

    resultados = []
    for k in range(k_min, k_max + 1):
        km = KMeans(n_clusters=k, random_state=42, n_init="auto")
        rotulos = km.fit_predict(X_scaled)
        inercia = km.inertia_
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            sil = silhouette_score(X_scaled, rotulos) if k > 1 else float("nan")
        resultados.append({"k": k, "inercia": inercia, "silhouette": sil})

    return pd.DataFrame(resultados)


# ---------------------------------------------------------------------------
# Etapa 4 — Aplicar o modelo K-Means
# ---------------------------------------------------------------------------


def aplica_kmeans(
    perfil: pd.DataFrame,
    X_scaled: np.ndarray,
    n_clusters: int = 4,
) -> pd.DataFrame:

    km = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
    perfil = perfil.copy()
    perfil["Cluster"] = km.fit_predict(X_scaled).astype(str)
    perfil["Cluster_label"] = perfil["Cluster"].map(
        lambda c: ROTULOS_CLUSTER.get(c, f"Grupo {c}")
    )
    return perfil


# ---------------------------------------------------------------------------
# Etapa 5 — Propagação dos clusters para o DataFrame original
# ---------------------------------------------------------------------------


def propaga_clusters(
    df_original: pd.DataFrame,
    perfil_clusterizado: pd.DataFrame,
) -> pd.DataFrame:

    mapa = perfil_clusterizado[["id_cliente", "Cluster", "Cluster_label"]]
    return df_original.merge(mapa, on="id_cliente", how="left")


# ---------------------------------------------------------------------------
# Etapa 6 — Resumo e métricas por cluster
# ---------------------------------------------------------------------------


def agrega_por_cluster(df_com_cluster: pd.DataFrame) -> pd.DataFrame:

    resumo = (
        df_com_cluster.groupby("Cluster_label")
        .agg(
            Vendas=("Preço", "size"),
            Receita_Total=("Preço", "sum"),
            Ticket_Médio=("Preço", "mean"),
            Frete_Médio=("Frete", "mean"),
            Parcelas_Médias=("Quantidade de parcelas", "mean"),
            Avaliação_Média=("Avaliação da compra", "mean"),
            Estados=("Local da compra", lambda x: ", ".join(sorted(x.unique()))),
        )
        .reset_index()
        .rename(columns={"Cluster_label": "Cluster"})
        .sort_values("Receita_Total", ascending=False)
        .round(2)
    )
    return resumo


# ---------------------------------------------------------------------------
# Pipeline completo — ponto de entrada único
# ---------------------------------------------------------------------------


def pipeline_completo(
    df: pd.DataFrame,
    n_clusters: int = 4,
    features: list[str] = FEATURES_PADRAO,
    calcular_elbow: bool = True,
    k_max_elbow: int = 8,
) -> dict[str, Any]:

    # Passo 1: identificar mercados por lat/lon
    df_id = cria_id_cliente(df)

    # Passo 2: resumir por mercado regional
    perfil = resume_por_cliente(df_id)
    n_mercados = len(perfil)

    # Passo 3: normalizar features
    X_scaled, scaler = prepara_features(perfil, features=features)

    # Passo 4: curva do cotovelo (opcional)
    metricas_elbow = None
    if calcular_elbow:
        k_max = min(k_max_elbow, n_mercados - 1)
        metricas_elbow = calcula_elbow(X_scaled, k_min=2, k_max=k_max)

    # Passo 5: aplicar K-Means
    n_clusters = min(n_clusters, n_mercados)
    perfil_clusterizado = aplica_kmeans(perfil, X_scaled, n_clusters=n_clusters)

    # Passo 6: propagar para as transações originais
    df_com_clusters = propaga_clusters(df_id, perfil_clusterizado)

    # Passo 7: gerar resumo por cluster
    resumo = agrega_por_cluster(df_com_clusters)

    return {
        "df_com_clusters": df_com_clusters,
        "perfil_clusters": perfil_clusterizado,
        "resumo_clusters": resumo,
        "metricas_elbow": metricas_elbow,
        "n_mercados": n_mercados,
        "features_usadas": features,
        "n_clusters": n_clusters,
    }


# Execução direta

if __name__ == "__main__":
    import requests

    SEP = "─" * 60

    print(SEP)
    print("  CLUSTERIZAÇÃO DE MERCADOS REGIONAIS — LabDados")
    print(SEP)

    # ── Carrega e prepara os dados ──────────────────────────────
    print("\n📥 Baixando dados da API...")
    response = requests.get("https://labdados.com/produtos", timeout=20)
    response.raise_for_status()

    df = pd.DataFrame(response.json())
    df["Data da Compra"] = pd.to_datetime(
        df["Data da Compra"], format="%d/%m/%Y", errors="coerce"
    )
    print(f"   {len(df):,} transações carregadas.\n")

    # ── Roda o pipeline completo ────────────────────────────────
    N_CLUSTERS = 6  # altere aqui para testar outros valores
    print(f"⚙️  Rodando pipeline com k={N_CLUSTERS}...")
    resultado = pipeline_completo(
        df,
        n_clusters=N_CLUSTERS,
        calcular_elbow=True,
        k_max_elbow=8,
    )

    # ── Metadados ───────────────────────────────────────────────
    print(f"\n{SEP}")
    print("  METADADOS")
    print(SEP)
    print(f"  Mercados regionais únicos : {resultado['n_mercados']}")
    print(f"  Clusters gerados          : {resultado['n_clusters']}")
    print(f"  Features usadas           : {', '.join(resultado['features_usadas'])}")

    # ── Elbow Method ────────────────────────────────────────────
    print(f"\n{SEP}")
    print("  ELBOW METHOD (inércia + silhouette por k)")
    print(SEP)
    elbow = resultado["metricas_elbow"]
    melhor_k = int(elbow.loc[elbow["silhouette"].idxmax(), "k"])
    print(f"  {'k':>4}  {'Inércia':>12}  {'Silhouette':>12}  {'':>6}")
    for _, linha in elbow.iterrows():
        k_val = int(linha["k"])
        marcador = "◀ melhor" if k_val == melhor_k else ""
        print(
            f"  {k_val:>4}  {linha['inercia']:>12.2f}  "
            f"{linha['silhouette']:>12.4f}  {marcador}"
        )
    print(f"\n  💡 k sugerido pelo Silhouette: {melhor_k}")

    # ── Resumo por cluster ──────────────────────────────────────
    print(f"\n{SEP}")
    print("  RESUMO POR CLUSTER")
    print(SEP)
    resumo = resultado["resumo_clusters"]
    for _, row in resumo.iterrows():
        print(f"\n  📦 {row['Cluster']}")
        print(f"     Vendas          : {int(row['Vendas']):,}")
        print(f"     Receita total   : R$ {row['Receita_Total']:>12,.2f}")
        print(f"     Ticket médio    : R$ {row['Ticket_Médio']:>8,.2f}")
        print(f"     Frete médio     : R$ {row['Frete_Médio']:>8,.2f}")
        print(f"     Parcelas médias : {row['Parcelas_Médias']:.2f}")
        print(f"     Avaliação média : {row['Avaliação_Média']:.2f} / 5")
        print(f"     Estados         : {row['Estados']}")

    # ── Amostra das primeiras transações clusterizadas ──────────
    print(f"\n{SEP}")
    print("  AMOSTRA — primeiras 5 transações com cluster atribuído")
    print(SEP)
    colunas_exibir = [
        "Produto", "Categoria do Produto", "Preço",
        "Local da compra", "Cluster_label",
    ]
    print(
        resultado["df_com_clusters"][colunas_exibir]
        .head(5)
        .to_string(index=False)
    )

    print(f"\n{SEP}")
    print("  ✅ Pipeline concluído com sucesso.")
    print(SEP)
