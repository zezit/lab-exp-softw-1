from pathlib import Path

import matplotlib
import pandas as pd
import seaborn as sns

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT_DIR = Path(__file__).resolve().parents[2]
DATASET_PATH = ROOT_DIR / "data" / "repos.csv"
FIGURES_DIR = ROOT_DIR / "reports" / "figures"


def configure_plot_style() -> None:
    sns.set_theme(style="whitegrid", context="notebook")
    plt.rcParams.update(
        {
            "axes.titlesize": 12,
            "axes.labelsize": 11,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "figure.titlesize": 13,
        }
    )


def load_and_prepare_data(dataset_path: Path) -> tuple[pd.DataFrame, pd.Timestamp]:
    df = pd.read_csv(dataset_path)

    required_columns = {
        "createdAt",
        "updatedAt",
        "pullRequests_count",
        "releases_count",
    }
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Colunas ausentes em {dataset_path}: {missing}")

    df["createdAt"] = pd.to_datetime(df["createdAt"], utc=True, errors="coerce")
    df["updatedAt"] = pd.to_datetime(df["updatedAt"], utc=True, errors="coerce")
    df["pullRequests_count"] = pd.to_numeric(df["pullRequests_count"], errors="coerce").fillna(0)
    df["releases_count"] = pd.to_numeric(df["releases_count"], errors="coerce").fillna(0)

    if "collectedAt" in df.columns:
        df["collectedAt"] = pd.to_datetime(df["collectedAt"], utc=True, errors="coerce")
        reference_date = df["collectedAt"].max()
    else:
        reference_date = df["updatedAt"].max()
    if pd.isna(reference_date):
        raise ValueError("Não foi possível calcular reference_date.")

    df = df.dropna(subset=["createdAt", "updatedAt"]).copy()
    df["age_days"] = (reference_date - df["createdAt"]).dt.days.clip(lower=0)
    df["age_years"] = df["age_days"] / 365.25
    df["days_since_update"] = (reference_date - df["updatedAt"]).dt.days.clip(lower=0)

    return df, reference_date


def save_figure(fig: plt.Figure, filename: str) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    output_path = FIGURES_DIR / filename
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Gerado: {output_path}")


def plot_rq01_repository_age_distribution(df: pd.DataFrame, reference_date: pd.Timestamp) -> None:
    ages_years = df["age_years"].dropna()
    summary = ages_years.describe(percentiles=[0.25, 0.5, 0.75])

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    sns.histplot(ages_years, bins=30, kde=True, color="#4C72B0", ax=axes[0])
    axes[0].set_title("Histograma da Idade dos Repositórios")
    axes[0].set_xlabel("Idade (anos)")
    axes[0].set_ylabel("Quantidade de repositórios")
    axes[0].grid(alpha=0.3)

    sns.boxplot(x=ages_years, color="#55A868", ax=axes[1])
    axes[1].set_title("Box Plot da Idade dos Repositórios")
    axes[1].set_xlabel("Idade (anos)")
    axes[1].grid(alpha=0.3)

    fig.suptitle(
        (
            "RQ01 — Distribuição da idade dos repositórios populares\n"
            f"reference_date={reference_date.date()} | "
            f"Q1={summary['25%']:.2f}, Mediana={summary['50%']:.2f}, Q3={summary['75%']:.2f} anos"
        )
    )
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    save_figure(fig, "rq01_repository_age_distribution.png")


def plot_rq02_pull_requests_distribution(df: pd.DataFrame, reference_date: pd.Timestamp) -> None:
    prs = df["pullRequests_count"].dropna()
    prs_positive = prs[prs > 0]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    if prs_positive.empty:
        for ax in axes:
            ax.text(0.5, 0.5, "Sem dados de PR > 0", ha="center", va="center", transform=ax.transAxes)
            ax.axis("off")
    else:
        sns.histplot(prs_positive, bins=40, color="#C44E52", ax=axes[0])
        axes[0].set_xscale("log")
        axes[0].set_title("Histograma de PRs aceitas (escala log)")
        axes[0].set_xlabel("Pull requests aceitas (log)")
        axes[0].set_ylabel("Quantidade de repositórios")
        axes[0].grid(alpha=0.3)

        sns.boxplot(x=prs_positive, color="#8172B3", ax=axes[1])
        axes[1].set_xscale("log")
        axes[1].set_title("Box Plot de PRs aceitas (escala log)")
        axes[1].set_xlabel("Pull requests aceitas (log)")
        axes[1].grid(alpha=0.3)

    zero_pr_share = (prs == 0).mean() * 100 if len(prs) > 0 else 0
    fig.suptitle(
        (
            "RQ02 — Distribuição de pull requests aceitas\n"
            f"reference_date={reference_date.date()} | Repositórios sem PR: {zero_pr_share:.1f}%"
        )
    )
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    save_figure(fig, "rq02_pull_requests_distribution.png")


def plot_rq03_releases_distribution(df: pd.DataFrame, reference_date: pd.Timestamp) -> None:
    releases = df["releases_count"].dropna()
    releases_positive = releases[releases > 0]

    labels = ["Sem releases (0)", "Poucas (1-10)", "Moderado (11-100)", "Muitas (100+)"]
    release_category = pd.cut(
        releases,
        bins=[-0.1, 0, 10, 100, float("inf")],
        labels=labels,
        include_lowest=True,
    )
    category_counts = release_category.value_counts().reindex(labels, fill_value=0)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    if releases_positive.empty:
        axes[0].text(0.5, 0.5, "Sem dados de releases > 0", ha="center", va="center", transform=axes[0].transAxes)
        axes[0].axis("off")
    else:
        sns.histplot(releases_positive, bins=35, color="#64B5CD", ax=axes[0])
        axes[0].set_xscale("log")
        axes[0].set_title("Histograma de releases (escala log)")
        axes[0].set_xlabel("Total de releases (log)")
        axes[0].set_ylabel("Quantidade de repositórios")
        axes[0].grid(alpha=0.3)

    sns.barplot(x=category_counts.values, y=category_counts.index, palette="viridis", ax=axes[1], hue=category_counts.index, legend=False)
    axes[1].set_title("Categorias de releases")
    axes[1].set_xlabel("Quantidade de repositórios")
    axes[1].set_ylabel("Categoria")
    axes[1].grid(alpha=0.3, axis="x")
    max_count = max(category_counts.max(), 1)
    for index, value in enumerate(category_counts.values):
        axes[1].text(value + max_count * 0.01, index, str(int(value)), va="center")

    fig.suptitle(
        (
            "RQ03 — Distribuição do total de releases\n"
            f"reference_date={reference_date.date()} | Mediana de releases={releases.median():.1f}"
        )
    )
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    save_figure(fig, "rq03_releases_distribution.png")


def update_frequency_category(days_since_update: float) -> str:
    if days_since_update == 0:
        return "Hoje (0)"
    if days_since_update <= 7:
        return "Semana (1-7)"
    if days_since_update <= 30:
        return "Mês (8-30)"
    if days_since_update <= 90:
        return "Trimestre (31-90)"
    if days_since_update <= 365:
        return "Ano (91-365)"
    return "Mais (>365)"


def plot_rq04_update_frequency(df: pd.DataFrame, reference_date: pd.Timestamp) -> None:
    days_since_update = df["days_since_update"].dropna()

    ordered_labels = [
        "Hoje (0)",
        "Semana (1-7)",
        "Mês (8-30)",
        "Trimestre (31-90)",
        "Ano (91-365)",
        "Mais (>365)",
    ]
    frequency_category = days_since_update.apply(update_frequency_category)
    category_counts = frequency_category.value_counts().reindex(ordered_labels, fill_value=0)
    category_percent = (category_counts / category_counts.sum() * 100).round(2)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    sns.barplot(
        x=category_percent.values,
        y=category_percent.index,
        palette="Blues_r",
        ax=axes[0],
        hue=category_percent.index,
        legend=False,
    )
    axes[0].set_title("Percentual por faixa de atualização")
    axes[0].set_xlabel("Percentual de repositórios (%)")
    axes[0].set_ylabel("Faixa de atualização")
    axes[0].grid(alpha=0.3, axis="x")
    for index, value in enumerate(category_percent.values):
        axes[0].text(value + 0.3, index, f"{value:.1f}%", va="center")

    sns.boxplot(x=days_since_update, color="#DD8452", ax=axes[1])
    axes[1].set_title("Box Plot de dias desde a última atualização")
    axes[1].set_xlabel("Dias desde a última atualização")
    axes[1].grid(alpha=0.3)

    fig.suptitle(
        (
            "RQ04 — Frequência de atualização dos repositórios populares\n"
            f"reference_date={reference_date.date()} | Mediana={days_since_update.median():.1f} dias"
        )
    )
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    save_figure(fig, "rq04_update_frequency.png")


def main() -> None:
    configure_plot_style()
    dataframe, reference_date = load_and_prepare_data(DATASET_PATH)

    print(f"Dataset carregado: {DATASET_PATH}")
    print(f"Repositórios válidos para análise: {len(dataframe)}")
    print(f"reference_date (collectedAt) = {reference_date}")

    plot_rq01_repository_age_distribution(dataframe, reference_date)
    plot_rq02_pull_requests_distribution(dataframe, reference_date)
    plot_rq03_releases_distribution(dataframe, reference_date)
    plot_rq04_update_frequency(dataframe, reference_date)

    print("Concluído: visualizações de RQ01-RQ04 geradas.")


if __name__ == "__main__":
    main()
