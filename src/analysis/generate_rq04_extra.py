"""
RQ04 — Análise complementar: repositórios NÃO atualizados no dia da coleta.
Gera tabela e scatter plot mostrando posição no ranking de estrelas.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
from pathlib import Path

matplotlib.use("Agg")
sns.set_theme(style="whitegrid")

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_PATH = BASE_DIR / "data" / "repos.csv"
FIG_DIR = BASE_DIR / "reports" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

DPI = 300


def load_and_prepare() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df["updatedAt"] = pd.to_datetime(df["updatedAt"])
    df["collectedAt"] = pd.to_datetime(df["collectedAt"])
    df["createdAt"] = pd.to_datetime(df["createdAt"])

    reference_date = df["collectedAt"].max()
    df["days_since_update"] = (reference_date - df["updatedAt"]).dt.days

    df = df.sort_values("stargazerCount", ascending=False).reset_index(drop=True)
    df["star_rank"] = df.index + 1
    return df, reference_date


def generate_table(df: pd.DataFrame, reference_date: pd.Timestamp):
    """Tabela com os repositórios que NÃO foram atualizados no dia da coleta."""
    not_recent = (
        df[df["days_since_update"] > 0]
        .sort_values("days_since_update", ascending=False)
        .copy()
    )

    table_data = not_recent[
        [
            "star_rank",
            "name",
            "primaryLanguage",
            "stargazerCount",
            "days_since_update",
            "pullRequests_count",
            "releases_count",
            "mentionable_users_count",
        ]
    ].values.tolist()

    col_labels = [
        "Rank\n(estrelas)",
        "Repositório",
        "Linguagem",
        "Estrelas",
        "Dias sem\natualização",
        "PRs",
        "Releases",
        "Contribuidores",
    ]

    fig, ax = plt.subplots(figsize=(14, 0.6 * len(table_data) + 2.4))
    ax.axis("off")
    ax.set_title(
        f"Repositórios NÃO atualizados no dia da coleta ({reference_date.strftime('%Y-%m-%d')})\n"
        f"Total: {len(not_recent)} de {len(df)} repositórios",
        fontsize=14,
        fontweight="bold",
        pad=18,
    )

    table = ax.table(
        cellText=table_data,
        colLabels=col_labels,
        loc="center",
        cellLoc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.6)

    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_facecolor("#4472C4")
            cell.set_text_props(color="white", fontweight="bold")
        elif row % 2 == 0:
            cell.set_facecolor("#D9E2F3")
        else:
            cell.set_facecolor("#EDF2FA")
        cell.set_edgecolor("#B0B0B0")
        if col == 1:
            cell.set_text_props(ha="left")
            cell._loc = "left"

    fig.tight_layout()
    path = FIG_DIR / "rq04_not_recently_updated.png"
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"✔ Tabela salva em {path}")


def generate_scatter(df: pd.DataFrame):
    """Scatter: star_rank (x) vs days_since_update (y), destaques anotados."""
    recent = df[df["days_since_update"] == 0]
    not_recent = df[df["days_since_update"] > 0]

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.scatter(
        recent["star_rank"],
        recent["days_since_update"],
        alpha=0.3,
        s=20,
        color="#4472C4",
        label=f"Atualizados no dia da coleta (n={len(recent)})",
        zorder=2,
    )
    ax.scatter(
        not_recent["star_rank"],
        not_recent["days_since_update"],
        s=80,
        color="#E74C3C",
        edgecolors="black",
        linewidths=0.8,
        marker="D",
        label=f"NÃO atualizados no dia da coleta (n={len(not_recent)})",
        zorder=3,
    )

    for _, row in not_recent.iterrows():
        ax.annotate(
            row["name"],
            (row["star_rank"], row["days_since_update"]),
            textcoords="offset points",
            xytext=(8, 4),
            fontsize=7,
            fontstyle="italic",
            color="#333333",
            arrowprops=dict(arrowstyle="-", color="#999999", lw=0.5),
        )

    ax.set_xlabel("Posição no ranking de estrelas", fontsize=12)
    ax.set_ylabel("Dias desde a última atualização", fontsize=12)
    ax.set_title(
        "RQ4 — Posição no ranking vs. dias sem atualização\n"
        "Repositórios raramente atualizados estão na metade inferior do ranking",
        fontsize=13,
        fontweight="bold",
    )
    ax.legend(loc="upper left", fontsize=9)
    ax.set_xlim(0, len(df) + 20)

    fig.tight_layout()
    path = FIG_DIR / "rq04_rank_vs_update.png"
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"✔ Scatter salvo em {path}")


def print_analysis(df: pd.DataFrame, reference_date: pd.Timestamp):
    """Imprime análise dos repos não atualizados recentemente."""
    not_recent = df[df["days_since_update"] > 0].sort_values(
        "days_since_update", ascending=False
    )
    total = len(df)
    n = len(not_recent)

    print("\n" + "=" * 70)
    print("RQ4 — REPOSITÓRIOS NÃO ATUALIZADOS NO DIA DA COLETA")
    print(f"Data de referência: {reference_date.strftime('%Y-%m-%d')}")
    print(f"Total: {n} de {total} ({100*n/total:.1f}%)")
    print("=" * 70)

    for _, r in not_recent.iterrows():
        age_years = (reference_date - r["createdAt"]).days / 365.25
        print(
            f"  #{r['star_rank']:>4}  {r['name']:<40} "
            f"lang={r['primaryLanguage']:<18} "
            f"★{r['stargazerCount']:>6,}  "
            f"dias={r['days_since_update']}  "
            f"idade={age_years:.1f}a  "
            f"PRs={r['pullRequests_count']}  "
            f"releases={r['releases_count']}"
        )

    # Características comuns
    print("\n— Características comuns —")

    ranks = not_recent["star_rank"]
    print(f"  Posições no ranking: {ranks.min()}–{ranks.max()} (mediana {ranks.median():.0f})")
    print(f"  → Todos na metade {'inferior' if ranks.median() > total / 2 else 'superior'} do ranking")

    lang_counts = not_recent["primaryLanguage"].value_counts()
    print(f"  Linguagens: {dict(lang_counts)}")

    ages = ((reference_date - not_recent["createdAt"]).dt.days / 365.25)
    print(f"  Idade: {ages.min():.1f}–{ages.max():.1f} anos (mediana {ages.median():.1f})")

    avg_stars_not = not_recent["stargazerCount"].mean()
    avg_stars_all = df["stargazerCount"].mean()
    print(f"  Estrelas (média): {avg_stars_not:,.0f} vs {avg_stars_all:,.0f} (geral)")

    avg_prs_not = not_recent["pullRequests_count"].mean()
    avg_prs_all = df["pullRequests_count"].mean()
    print(f"  PRs (média): {avg_prs_not:,.0f} vs {avg_prs_all:,.0f} (geral)")

    avg_rel_not = not_recent["releases_count"].mean()
    avg_rel_all = df["releases_count"].mean()
    print(f"  Releases (média): {avg_rel_not:,.1f} vs {avg_rel_all:,.1f} (geral)")

    print("=" * 70)


def main():
    df, reference_date = load_and_prepare()
    generate_table(df, reference_date)
    generate_scatter(df)
    print_analysis(df, reference_date)


if __name__ == "__main__":
    main()
