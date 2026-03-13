"""Visualizações extras para RQ2 — entender a heterogeneidade de PRs."""

from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

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


def load_data() -> tuple[pd.DataFrame, pd.Timestamp]:
    df = pd.read_csv(DATASET_PATH)
    df["createdAt"] = pd.to_datetime(df["createdAt"], utc=True, errors="coerce")
    df["collectedAt"] = pd.to_datetime(df["collectedAt"], utc=True, errors="coerce")
    df["pullRequests_count"] = pd.to_numeric(df["pullRequests_count"], errors="coerce").fillna(0)
    df["mentionable_users_count"] = pd.to_numeric(df["mentionable_users_count"], errors="coerce").fillna(0)

    reference_date = df["collectedAt"].max()
    df["age_years"] = (reference_date - df["createdAt"]).dt.days / 365.25

    return df, reference_date


def _age_bin(age: float) -> str:
    if age < 2:
        return "0–2 anos"
    elif age < 5:
        return "2–5 anos"
    elif age < 10:
        return "5–10 anos"
    else:
        return "10+ anos"


def _contributor_bin(n: float) -> str:
    if n <= 10:
        return "1–10"
    elif n <= 50:
        return "11–50"
    elif n <= 200:
        return "51–200"
    else:
        return "200+"


# ── Figure 1: PRs by age range ──────────────────────────────────────────────
def plot_prs_by_age_range(df: pd.DataFrame) -> None:
    age_order = ["0–2 anos", "2–5 anos", "5–10 anos", "10+ anos"]
    df["age_range"] = df["age_years"].apply(_age_bin)
    df["age_range"] = pd.Categorical(df["age_range"], categories=age_order, ordered=True)

    counts = df["age_range"].value_counts().sort_index()
    labels = [f"{cat}\n(n={counts[cat]})" for cat in age_order]

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.boxplot(
        data=df, x="age_range", y="pullRequests_count",
        order=age_order, palette="Blues", ax=ax,
    )
    ax.set_yscale("log")
    ax.set_xticklabels(labels)
    ax.set_xlabel("Faixa de Idade do Repositório")
    ax.set_ylabel("Quantidade de Pull Requests (log)")
    ax.set_title("RQ2 — Distribuição de PRs por Faixa de Idade do Repositório")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "rq02_prs_by_age_range.png", dpi=300)
    plt.close(fig)
    print("✓ rq02_prs_by_age_range.png")


# ── Figure 2: PRs by language ───────────────────────────────────────────────
def plot_prs_by_language(df: pd.DataFrame) -> None:
    top8 = df["primaryLanguage"].value_counts().head(8).index.tolist()
    df["lang_group"] = df["primaryLanguage"].where(df["primaryLanguage"].isin(top8), "Outras")

    medians = df.groupby("lang_group")["pullRequests_count"].median().sort_values(ascending=False)
    order = medians.index.tolist()

    counts = df["lang_group"].value_counts()
    labels = [f"{lang}\n(n={counts[lang]})" for lang in order]

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.boxplot(
        data=df, x="lang_group", y="pullRequests_count",
        order=order, palette="Set2", ax=ax,
    )
    ax.set_yscale("log")
    ax.set_xticklabels(labels, rotation=30, ha="right")
    ax.set_xlabel("Linguagem Primária")
    ax.set_ylabel("Quantidade de Pull Requests (log)")
    ax.set_title("RQ2 — Distribuição de PRs por Linguagem (Top 8 + Outras)")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "rq02_prs_by_language.png", dpi=300)
    plt.close(fig)
    print("✓ rq02_prs_by_language.png")


# ── Figure 3: Contributors vs PRs scatter ───────────────────────────────────
def plot_contributors_vs_prs(df: pd.DataFrame) -> None:
    mask = (df["mentionable_users_count"] > 0) & (df["pullRequests_count"] > 0)
    dfs = df.loc[mask].copy()

    top5 = dfs["primaryLanguage"].value_counts().head(5).index.tolist()
    dfs["lang_color"] = dfs["primaryLanguage"].where(dfs["primaryLanguage"].isin(top5), "Other")

    rho, pval = stats.spearmanr(dfs["mentionable_users_count"], dfs["pullRequests_count"])

    fig, ax = plt.subplots(figsize=(8, 6))
    for lang in top5 + ["Other"]:
        sub = dfs[dfs["lang_color"] == lang]
        ax.scatter(
            sub["mentionable_users_count"], sub["pullRequests_count"],
            label=lang, alpha=0.6, s=20, edgecolors="none",
        )

    # Regression line on log-log scale
    log_x = np.log10(dfs["mentionable_users_count"].values)
    log_y = np.log10(dfs["pullRequests_count"].values)
    slope, intercept, *_ = stats.linregress(log_x, log_y)
    x_line = np.linspace(log_x.min(), log_x.max(), 100)
    y_line = slope * x_line + intercept
    ax.plot(10**x_line, 10**y_line, color="red", linewidth=2, linestyle="--", label="Regressão (log-log)")

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Contribuidores Mencionáveis (log)")
    ax.set_ylabel("Pull Requests (log)")
    ax.set_title(f"RQ2 — Contribuidores vs PRs (Spearman ρ = {rho:.3f}, p = {pval:.2e})")
    ax.legend(fontsize=8, loc="upper left")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "rq02_contributors_vs_prs.png", dpi=300)
    plt.close(fig)
    print(f"✓ rq02_contributors_vs_prs.png  (Spearman ρ = {rho:.3f})")


# ── Figure 4: PRs by contributor range ───────────────────────────────────────
def plot_prs_by_contributor_range(df: pd.DataFrame) -> None:
    contrib_order = ["1–10", "11–50", "51–200", "200+"]
    df["contrib_range"] = df["mentionable_users_count"].apply(_contributor_bin)
    df["contrib_range"] = pd.Categorical(df["contrib_range"], categories=contrib_order, ordered=True)

    counts = df["contrib_range"].value_counts().sort_index()
    labels = [f"{cat}\n(n={counts[cat]})" for cat in contrib_order]

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.boxplot(
        data=df, x="contrib_range", y="pullRequests_count",
        order=contrib_order, palette="Oranges", ax=ax,
    )
    ax.set_yscale("log")
    ax.set_xticklabels(labels)
    ax.set_xlabel("Faixa de Contribuidores Mencionáveis")
    ax.set_ylabel("Quantidade de Pull Requests (log)")
    ax.set_title("RQ2 — Distribuição de PRs por Faixa de Contribuidores")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "rq02_prs_by_contributor_range.png", dpi=300)
    plt.close(fig)
    print("✓ rq02_prs_by_contributor_range.png")


# ── Main ─────────────────────────────────────────────────────────────────────
def main() -> None:
    configure_plot_style()
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    df, ref = load_data()
    print(f"Dataset: {len(df)} repos | Data de referência: {ref.date()}")

    plot_prs_by_age_range(df.copy())
    plot_prs_by_language(df.copy())
    plot_contributors_vs_prs(df.copy())
    plot_prs_by_contributor_range(df.copy())

    print("\nTodas as figuras salvas em:", FIGURES_DIR)


if __name__ == "__main__":
    main()
