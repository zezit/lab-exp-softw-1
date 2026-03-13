"""Visualizações extras para RQ6: relação entre % de issues fechadas e
linguagem, idade do repositório e número de contribuidores."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from scipy import stats

ROOT_DIR = Path(__file__).resolve().parents[2]
DATASET_PATH = ROOT_DIR / "data" / "repos.csv"
FIGURES_DIR = ROOT_DIR / "reports" / "figures"


def load_and_prepare(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)

    df["primaryLanguage"] = (
        df["primaryLanguage"].fillna("Unknown").astype(str).str.strip().replace("", "Unknown")
    )

    for col in ["open_issues", "closed_issues", "stargazerCount", "mentionable_users_count"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["createdAt"] = pd.to_datetime(df["createdAt"], utc=True, errors="coerce")
    df["collectedAt"] = pd.to_datetime(df["collectedAt"], utc=True, errors="coerce")

    reference_date = df["collectedAt"].max()

    df["total_issues"] = df["open_issues"] + df["closed_issues"]
    df = df[df["total_issues"] > 0].copy()

    df["closed_issues_pct"] = df["closed_issues"] / df["total_issues"] * 100
    df["age_years"] = (reference_date - df["createdAt"]).dt.total_seconds() / (365.25 * 86400)

    df["age_range"] = pd.cut(
        df["age_years"],
        bins=[0, 2, 5, 10, float("inf")],
        labels=["0–2 anos", "2–5 anos", "5–10 anos", "10+ anos"],
        right=False,
    )

    return df


def plot_issues_by_language(df: pd.DataFrame) -> None:
    top10 = df["primaryLanguage"].value_counts().nlargest(10).index.tolist()
    subset = df[df["primaryLanguage"].isin(top10)].copy()

    lang_medians = subset.groupby("primaryLanguage")["closed_issues_pct"].median()
    order = lang_medians.sort_values(ascending=False).index.tolist()

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.boxplot(
        data=subset,
        x="primaryLanguage",
        y="closed_issues_pct",
        hue="primaryLanguage",
        order=order,
        hue_order=order,
        palette="Set2",
        legend=False,
        ax=ax,
    )
    ax.set_title("RQ6 — % de Issues Fechadas por Linguagem (Top 10)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Linguagem", fontsize=12)
    ax.set_ylabel("% de Issues Fechadas", fontsize=12)
    ax.tick_params(axis="x", rotation=30)
    ax.set_ylim(-5, 105)

    for i, lang in enumerate(order):
        med = lang_medians[lang]
        ax.text(i, med + 2, f"{med:.1f}%", ha="center", va="bottom", fontsize=9, fontweight="bold")

    fig.tight_layout()
    out = FIGURES_DIR / "rq06_issues_by_language.png"
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print(f"  ✓ Salvo: {out}")


def print_statistics(df: pd.DataFrame) -> None:
    print("\n" + "=" * 60)
    print("ESTATÍSTICAS — RQ6: Correlações e Rankings")
    print("=" * 60)

    rho_age, p_age = stats.spearmanr(df["age_years"], df["closed_issues_pct"])
    contributors = df[df["mentionable_users_count"] > 0]
    rho_contrib, p_contrib = stats.spearmanr(
        contributors["mentionable_users_count"], contributors["closed_issues_pct"]
    )
    rho_stars, p_stars = stats.spearmanr(df["stargazerCount"], df["closed_issues_pct"])

    print("\n📊 Correlações de Spearman:")
    print(f"  • Issues% vs Idade:          ρ = {rho_age:+.4f}  (p = {p_age:.2e})")
    print(f"  • Issues% vs Contribuidores:  ρ = {rho_contrib:+.4f}  (p = {p_contrib:.2e})")
    print(f"  • Issues% vs Stars:           ρ = {rho_stars:+.4f}  (p = {p_stars:.2e})")

    lang_medians = df.groupby("primaryLanguage")["closed_issues_pct"].median()
    lang_counts = df["primaryLanguage"].value_counts()
    # Considerar apenas linguagens com ≥ 5 repos
    valid_langs = lang_counts[lang_counts >= 5].index
    lang_medians = lang_medians[lang_medians.index.isin(valid_langs)].sort_values(ascending=False)

    print("\n🏆 Top 3 linguagens por mediana de issues fechadas (≥ 5 repos):")
    for i, (lang, med) in enumerate(lang_medians.head(3).items(), 1):
        n = lang_counts[lang]
        print(f"  {i}. {lang}: {med:.2f}%  (n={n})")

    print("\n⚠️  Bottom 3 linguagens por mediana de issues fechadas (≥ 5 repos):")
    for i, (lang, med) in enumerate(lang_medians.tail(3).items(), 1):
        n = lang_counts[lang]
        print(f"  {i}. {lang}: {med:.2f}%  (n={n})")

    print(f"\n📋 Repos analisados: {len(df)} (excluídos {1000 - len(df)} com 0 issues)")
    print("=" * 60)


def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    print("Carregando dataset...")
    df = load_and_prepare(DATASET_PATH)
    print(f"  → {len(df)} repos com issues (total_issues > 0)\n")

    print("Gerando gráficos RQ6 extras:")
    plot_issues_by_language(df)
    print_statistics(df)


if __name__ == "__main__":
    main()
