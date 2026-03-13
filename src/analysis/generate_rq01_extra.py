from pathlib import Path

import matplotlib
import numpy as np
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
        "stargazerCount",
        "pullRequests_count",
        "releases_count",
        "mentionable_users_count",
        "primaryLanguage",
    }
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Colunas ausentes em {dataset_path}: {missing}")

    df["createdAt"] = pd.to_datetime(df["createdAt"], utc=True, errors="coerce")
    df["stargazerCount"] = pd.to_numeric(df["stargazerCount"], errors="coerce").fillna(0)
    df["pullRequests_count"] = pd.to_numeric(df["pullRequests_count"], errors="coerce").fillna(0)
    df["releases_count"] = pd.to_numeric(df["releases_count"], errors="coerce").fillna(0)
    df["mentionable_users_count"] = pd.to_numeric(df["mentionable_users_count"], errors="coerce").fillna(0)

    if "collectedAt" in df.columns:
        df["collectedAt"] = pd.to_datetime(df["collectedAt"], utc=True, errors="coerce")
        reference_date = df["collectedAt"].max()
    else:
        df["updatedAt"] = pd.to_datetime(df["updatedAt"], utc=True, errors="coerce")
        reference_date = df["updatedAt"].max()
    if pd.isna(reference_date):
        raise ValueError("Não foi possível calcular reference_date.")

    df = df.dropna(subset=["createdAt"]).copy()
    df["age_years"] = (reference_date - df["createdAt"]).dt.days / 365.25

    return df, reference_date


def save_figure(fig: plt.Figure, filename: str) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    output_path = FIGURES_DIR / filename
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Gerado: {output_path}")


def plot_age_vs_stars_scatter(df: pd.DataFrame, reference_date: pd.Timestamp) -> None:
    """Scatter: Idade × Estrelas, cor = log(PRs), tamanho = contribuidores."""
    plot_df = df[df["stargazerCount"] > 0].copy()
    plot_df["log_prs"] = np.log1p(plot_df["pullRequests_count"])

    sizes = plot_df["mentionable_users_count"].clip(lower=1)
    size_scaled = (sizes / sizes.max()) * 200 + 10

    fig, ax = plt.subplots(figsize=(12, 7))
    scatter = ax.scatter(
        plot_df["age_years"],
        plot_df["stargazerCount"],
        c=plot_df["log_prs"],
        s=size_scaled,
        cmap="viridis",
        alpha=0.6,
        edgecolors="white",
        linewidths=0.3,
    )

    ax.set_yscale("log")
    ax.set_xlabel("Idade do repositório (anos)")
    ax.set_ylabel("Estrelas (escala log)")
    ax.set_title(
        "RQ01 — Idade × Estrelas dos repositórios populares\n"
        f"Cor = log(PRs aceitas) | Tamanho = contribuidores | ref={reference_date.date()}"
    )
    ax.grid(alpha=0.3)

    cbar = fig.colorbar(scatter, ax=ax, pad=0.02)
    cbar.set_label("log(1 + Pull Requests aceitas)")

    fig.tight_layout()
    save_figure(fig, "rq01_age_vs_stars_scatter.png")


def plot_correlation_matrix(df: pd.DataFrame, reference_date: pd.Timestamp) -> None:
    """Heatmap de correlação de Spearman entre métricas numéricas."""
    metrics = ["age_years", "stargazerCount", "pullRequests_count", "releases_count", "mentionable_users_count"]
    labels = ["Idade (anos)", "Estrelas", "PRs aceitas", "Releases", "Contribuidores"]

    corr_df = df[metrics].dropna()
    corr_matrix = corr_df.corr(method="spearman")

    fig, ax = plt.subplots(figsize=(8, 7))
    sns.heatmap(
        corr_matrix,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        vmin=-1,
        vmax=1,
        xticklabels=labels,
        yticklabels=labels,
        square=True,
        linewidths=0.5,
        ax=ax,
    )
    ax.set_title(
        "RQ01 — Matriz de correlação de Spearman\n"
        f"Métricas dos repositórios populares | n={len(corr_df)} | ref={reference_date.date()}"
    )

    fig.tight_layout()
    save_figure(fig, "rq01_correlation_matrix.png")


def plot_age_vs_contributors(df: pd.DataFrame, reference_date: pd.Timestamp) -> None:
    """Scatter: Idade × Contribuidores, cor = linguagem (top 5 + Outros)."""
    plot_df = df[df["mentionable_users_count"] > 0].copy()

    lang_col = "primaryLanguage"
    top5 = plot_df[lang_col].value_counts().head(5).index.tolist()
    plot_df["language_group"] = plot_df[lang_col].apply(lambda x: x if x in top5 else "Outros")

    order = top5 + ["Outros"]
    palette = sns.color_palette("tab10", n_colors=len(order))
    color_map = dict(zip(order, palette))

    fig, ax = plt.subplots(figsize=(12, 7))
    for lang in order:
        subset = plot_df[plot_df["language_group"] == lang]
        ax.scatter(
            subset["age_years"],
            subset["mentionable_users_count"],
            label=lang,
            color=color_map[lang],
            alpha=0.6,
            s=30,
            edgecolors="white",
            linewidths=0.3,
        )

    ax.set_yscale("log")
    ax.set_xlabel("Idade do repositório (anos)")
    ax.set_ylabel("Contribuidores (escala log)")
    ax.set_title(
        "RQ01 — Idade × Contribuidores por linguagem\n"
        f"Top 5 linguagens + Outros | ref={reference_date.date()}"
    )
    ax.legend(title="Linguagem", loc="upper left", framealpha=0.9)
    ax.grid(alpha=0.3)

    fig.tight_layout()
    save_figure(fig, "rq01_age_vs_contributors.png")


def main() -> None:
    configure_plot_style()
    dataframe, reference_date = load_and_prepare_data(DATASET_PATH)

    print(f"Dataset carregado: {DATASET_PATH}")
    print(f"Repositórios válidos para análise: {len(dataframe)}")
    print(f"reference_date (collectedAt) = {reference_date}")

    plot_age_vs_stars_scatter(dataframe, reference_date)
    plot_correlation_matrix(dataframe, reference_date)
    plot_age_vs_contributors(dataframe, reference_date)

    print("Concluído: visualizações extras de RQ01 geradas.")


if __name__ == "__main__":
    main()
