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

NON_SOFTWARE_LANGUAGES = {"Unknown", "Markdown", None, "", np.nan}


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


def load_data(dataset_path: Path) -> pd.DataFrame:
    df = pd.read_csv(dataset_path)
    df["releases_count"] = pd.to_numeric(df["releases_count"], errors="coerce").fillna(0)
    df["pullRequests_count"] = pd.to_numeric(df["pullRequests_count"], errors="coerce").fillna(0)
    df["stargazerCount"] = pd.to_numeric(df["stargazerCount"], errors="coerce").fillna(0)
    df["mentionable_users_count"] = pd.to_numeric(df["mentionable_users_count"], errors="coerce").fillna(0)
    df["primaryLanguage"] = df["primaryLanguage"].fillna("Unknown")
    return df


def save_figure(fig: plt.Figure, filename: str) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    output_path = FIGURES_DIR / filename
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Gerado: {output_path}")


def is_non_software(language: str) -> bool:
    return language in {"Unknown", "Markdown", ""}


def plot_zero_release_languages(df: pd.DataFrame, df_zero: pd.DataFrame) -> None:
    """Gráfico 1: distribuição de linguagens — repos sem releases vs todos."""
    top_langs_all = df["primaryLanguage"].value_counts().head(10).index.tolist()
    all_langs = set(top_langs_all) | set(df_zero["primaryLanguage"].value_counts().head(10).index.tolist())
    top_langs = [l for l in df["primaryLanguage"].value_counts().index if l in all_langs][:12]

    pct_all = (df["primaryLanguage"].value_counts(normalize=True) * 100).reindex(top_langs, fill_value=0)
    pct_zero = (df_zero["primaryLanguage"].value_counts(normalize=True) * 100).reindex(top_langs, fill_value=0)

    x = np.arange(len(top_langs))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    bars1 = ax.barh(x + width / 2, pct_all.values, width, label="Todos os repos", color="#4C72B0", alpha=0.85)
    bars2 = ax.barh(x - width / 2, pct_zero.values, width, label="Repos sem releases", color="#C44E52", alpha=0.85)

    ax.set_yticks(x)
    ax.set_yticklabels(top_langs)
    ax.set_xlabel("Percentual de repositórios (%)")
    ax.set_title("RQ03 — Distribuição de linguagens: repos sem releases vs todos")
    ax.legend(loc="lower right")
    ax.grid(alpha=0.3, axis="x")
    ax.invert_yaxis()

    for bar_group in [bars1, bars2]:
        for bar in bar_group:
            w = bar.get_width()
            if w > 0.5:
                ax.text(w + 0.3, bar.get_y() + bar.get_height() / 2, f"{w:.1f}%", va="center", fontsize=8)

    fig.tight_layout()
    save_figure(fig, "rq03_zero_release_languages.png")


def plot_top_zero_release_repos(df_zero: pd.DataFrame) -> None:
    """Gráfico 2: tabela com os top 30 repos sem releases."""
    top30 = (
        df_zero.sort_values("stargazerCount", ascending=False)
        .head(30)
        .reset_index(drop=True)
    )

    table_data = []
    cell_colors = []
    non_sw_color = "#FDDEDE"
    normal_color = "#FFFFFF"
    header_color = "#4C72B0"

    for i, row in top30.iterrows():
        rank = i + 1
        lang = str(row["primaryLanguage"])
        stars = f"{int(row['stargazerCount']):,}"
        prs = f"{int(row['pullRequests_count']):,}"
        users = f"{int(row['mentionable_users_count']):,}"
        name = str(row["name"])[:30]

        table_data.append([rank, name, lang, stars, prs, users])

        bg = non_sw_color if is_non_software(lang) else normal_color
        cell_colors.append([bg] * 6)

    col_labels = ["#", "Nome", "Linguagem", "Stars", "PRs", "Contribuidores"]

    fig, ax = plt.subplots(figsize=(12, 10))
    ax.axis("off")

    table = ax.table(
        cellText=table_data,
        colLabels=col_labels,
        cellColours=cell_colors,
        colColours=[header_color] * 6,
        loc="center",
        cellLoc="center",
    )

    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 1.3)

    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_text_props(color="white", fontweight="bold")
        if col == 1:
            cell.set_text_props(ha="left")
            cell._loc = "left"

    ax.set_title(
        "RQ03 — Top 30 repositórios populares sem releases\n"
        "(destacados em vermelho: prováveis repos não-software)",
        fontsize=12,
        fontweight="bold",
        pad=20,
    )

    fig.tight_layout()
    save_figure(fig, "rq03_zero_release_top_repos.png")


def plot_releases_by_language(df: pd.DataFrame) -> None:
    """Gráfico 3: barras empilhadas normalizadas — categorias de releases por linguagem."""
    top8 = df["primaryLanguage"].value_counts().head(8).index.tolist()
    df_top = df[df["primaryLanguage"].isin(top8)].copy()

    labels = ["0", "1–10", "11–100", "100+"]
    df_top["release_cat"] = pd.cut(
        df_top["releases_count"],
        bins=[-0.1, 0, 10, 100, float("inf")],
        labels=labels,
        include_lowest=True,
    )

    ct = pd.crosstab(df_top["primaryLanguage"], df_top["release_cat"], normalize="index") * 100
    ct = ct.reindex(columns=labels, fill_value=0)
    ct = ct.loc[top8]

    colors = ["#C44E52", "#F0A050", "#55A868", "#4C72B0"]
    fig, ax = plt.subplots(figsize=(10, 6))

    bottom = np.zeros(len(ct))
    for i, cat in enumerate(labels):
        values = ct[cat].values
        ax.barh(ct.index, values, left=bottom, label=cat, color=colors[i], alpha=0.85)
        for j, (v, b) in enumerate(zip(values, bottom)):
            if v > 5:
                ax.text(b + v / 2, j, f"{v:.0f}%", ha="center", va="center", fontsize=8, color="white", fontweight="bold")
        bottom += values

    ax.set_xlabel("Percentual de repositórios (%)")
    ax.set_title("RQ03 — Categorias de releases por linguagem (top 8)")
    ax.legend(title="Releases", loc="lower right")
    ax.grid(alpha=0.3, axis="x")
    ax.invert_yaxis()

    fig.tight_layout()
    save_figure(fig, "rq03_releases_by_language.png")


def print_console_summary(df: pd.DataFrame, df_zero: pd.DataFrame) -> None:
    total = len(df)
    n_zero = len(df_zero)
    pct_zero = n_zero / total * 100

    non_sw = df_zero[df_zero["primaryLanguage"].apply(is_non_software)]
    n_non_sw = len(non_sw)

    common_langs = {"Python", "JavaScript", "TypeScript", "Java", "C++", "C", "Go",
                    "Rust", "C#", "PHP", "Ruby", "Swift", "Kotlin", "Dart", "Shell"}
    sw_zero = df_zero[df_zero["primaryLanguage"].isin(common_langs)]
    n_sw_zero = len(sw_zero)

    print("\n" + "=" * 60)
    print("RQ03 — Análise complementar: repos sem releases")
    print("=" * 60)
    print(f"Total de repositórios: {total}")
    print(f"Repos sem releases: {n_zero} ({pct_zero:.1f}%)")
    print(f"  → Prováveis não-software (Unknown/Markdown): {n_non_sw}")
    print(f"  → Em linguagens de programação comuns: {n_sw_zero}")
    print(f"  → Outros: {n_zero - n_non_sw - n_sw_zero}")
    print()
    print("Top 10 linguagens nos repos sem releases:")
    lang_counts = df_zero["primaryLanguage"].value_counts().head(10)
    for lang, count in lang_counts.items():
        print(f"  {lang:20s} {count:4d} ({count / n_zero * 100:.1f}%)")
    print("=" * 60)


def main() -> None:
    configure_plot_style()
    df = load_data(DATASET_PATH)
    df_zero = df[df["releases_count"] == 0].copy()

    print(f"Dataset carregado: {DATASET_PATH}")
    print(f"Total de repositórios: {len(df)}")

    print_console_summary(df, df_zero)
    plot_zero_release_languages(df, df_zero)
    plot_top_zero_release_repos(df_zero)
    plot_releases_by_language(df)

    print("\nConcluído: visualizações extras de RQ03 geradas.")


if __name__ == "__main__":
    main()
