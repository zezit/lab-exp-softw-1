from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


ROOT_DIR = Path(__file__).resolve().parents[2]
DATASET_PATH = ROOT_DIR / "data" / "repos.csv"
FIGURES_DIR = ROOT_DIR / "reports" / "figures"


def load_dataset(csv_path: Path) -> tuple[pd.DataFrame, pd.Timestamp]:
    df = pd.read_csv(csv_path)

    required_columns = [
        "name",
        "updatedAt",
        "primaryLanguage",
        "releases_count",
        "pullRequests_count",
        "open_issues",
        "closed_issues",
    ]
    missing_columns = [column for column in required_columns if column not in df.columns]
    if missing_columns:
        raise ValueError(f"Colunas obrigatórias ausentes no dataset: {missing_columns}")

    df["primaryLanguage"] = (
        df["primaryLanguage"].fillna("Unknown").astype(str).str.strip().replace("", "Unknown")
    )

    numeric_columns = ["releases_count", "pullRequests_count", "open_issues", "closed_issues"]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0)

    df["updatedAt"] = pd.to_datetime(df["updatedAt"], errors="coerce", utc=True)
    if df["updatedAt"].isna().all():
        raise ValueError("Não foi possível interpretar valores válidos na coluna updatedAt.")

    if "collectedAt" in df.columns:
        df["collectedAt"] = pd.to_datetime(df["collectedAt"], utc=True, errors="coerce")
        reference_date = df["collectedAt"].max()
    else:
        reference_date = df["updatedAt"].max()
    df["days_since_update"] = (reference_date - df["updatedAt"]).dt.total_seconds() / 86400
    df["days_since_update"] = df["days_since_update"].clip(lower=0)

    total_issues = df["open_issues"] + df["closed_issues"]
    df["closed_issues_percentage"] = np.where(
        total_issues > 0,
        (df["closed_issues"] / total_issues) * 100,
        np.nan,
    )

    return df, reference_date


def plot_rq05_primary_languages(df: pd.DataFrame, output_file: Path, top_n: int = 12) -> None:
    language_counts = df["primaryLanguage"].value_counts()
    top_languages = language_counts.head(top_n)
    others_count = language_counts.iloc[top_n:].sum()

    if others_count > 0:
        top_languages.loc["Outras"] = others_count

    ranking = top_languages.sort_values(ascending=True)

    fig, ax = plt.subplots(figsize=(12, 8))
    sns.barplot(x=ranking.values, y=ranking.index, ax=ax, color="#3B82F6")

    total_repositories = ranking.sum()
    for index, count in enumerate(ranking.values):
        percentage = (count / total_repositories) * 100 if total_repositories > 0 else 0
        ax.text(
            count + (ranking.max() * 0.01),
            index,
            f"{int(count)} ({percentage:.1f}%)",
            va="center",
            fontsize=9,
        )

    ax.set_title("RQ05 — Ranking de Linguagens Primárias")
    ax.set_xlabel("Quantidade de Repositórios")
    ax.set_ylabel("Linguagem Primária")

    fig.tight_layout()
    fig.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_rq06_closed_issues(df: pd.DataFrame, output_file: Path) -> None:
    closed_issues_percentage = df["closed_issues_percentage"].dropna()
    if closed_issues_percentage.empty:
        raise ValueError("Nenhum repositório com issues para calcular o percentual de issues fechadas.")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5), gridspec_kw={"width_ratios": [3, 1]})

    sns.histplot(
        closed_issues_percentage,
        bins=np.arange(0, 110, 10),
        kde=True,
        color="#10B981",
        ax=axes[0],
    )
    median_value = closed_issues_percentage.median()
    axes[0].axvline(
        median_value,
        color="#DC2626",
        linestyle="--",
        linewidth=2,
        label=f"Mediana: {median_value:.1f}%",
    )
    axes[0].set_xlim(0, 100)
    axes[0].set_title("Distribuição do Percentual de Issues Fechadas")
    axes[0].set_xlabel("% de Issues Fechadas")
    axes[0].set_ylabel("Quantidade de Repositórios")
    axes[0].legend(loc="upper left")

    sns.boxplot(y=closed_issues_percentage, color="#A78BFA", ax=axes[1])
    axes[1].set_ylim(0, 100)
    axes[1].set_title("Box Plot")
    axes[1].set_ylabel("% de Issues Fechadas")

    fig.tight_layout()
    fig.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_rq07_contribution_by_language(
    df: pd.DataFrame,
    output_file: Path,
    reference_date: pd.Timestamp,
    top_n: int = 10,
) -> None:
    top_languages = df["primaryLanguage"].value_counts().head(top_n).index.tolist()
    language_subset = df[df["primaryLanguage"].isin(top_languages)].copy()

    if language_subset.empty:
        raise ValueError("Não há dados suficientes para gerar a análise da RQ07.")

    summary = (
        language_subset.groupby("primaryLanguage", as_index=True)
        .agg(
            median_pull_requests=("pullRequests_count", "median"),
            median_releases=("releases_count", "median"),
            median_days_since_update=("days_since_update", "median"),
        )
        .reindex(top_languages)
    )

    fig, axes = plt.subplots(1, 3, figsize=(24, 7))
    plot_config = [
        ("median_pull_requests", "Mediana de Pull Requests", "#2563EB"),
        ("median_releases", "Mediana de Releases", "#F59E0B"),
        ("median_days_since_update", "Mediana de Dias desde Atualização", "#14B8A6"),
    ]

    for axis, (column, title, color) in zip(axes, plot_config):
        sns.barplot(
            x=summary.index,
            y=summary[column].values,
            ax=axis,
            color=color,
        )
        axis.set_title(title)
        axis.set_xlabel("Linguagem Primária")
        axis.tick_params(axis="x", rotation=35)

    axes[0].set_ylabel("Pull Requests")
    axes[1].set_ylabel("Releases")
    axes[2].set_ylabel("Dias")
    fig.suptitle(
        f"RQ07 — Comparação por Linguagem (Top {top_n}) | referência: {reference_date.date()}",
        fontsize=14,
        y=1.02,
    )

    fig.tight_layout()
    fig.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    sns.set_theme(style="whitegrid")
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    df, reference_date = load_dataset(DATASET_PATH)

    plot_rq05_primary_languages(
        df=df,
        output_file=FIGURES_DIR / "rq05_primary_languages_ranking.png",
    )
    plot_rq06_closed_issues(
        df=df,
        output_file=FIGURES_DIR / "rq06_closed_issues_percentage.png",
    )
    plot_rq07_contribution_by_language(
        df=df,
        output_file=FIGURES_DIR / "rq07_contribution_by_language.png",
        reference_date=reference_date,
    )

    print("Visualizações RQ05–RQ07 geradas com sucesso em reports/figures/.")


if __name__ == "__main__":
    main()
