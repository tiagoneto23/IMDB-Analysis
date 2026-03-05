"""
imdb_viz.py — Interactive IMDB Visualizations (Tkinter wrapper)
Saves all charts as PNGs to plots/.

Charts:
  C1  Rating por género          [correto]
  C2  Filmes por década          [correto]
  E1  Revenue médio por género   [enganoso]
  E2  Duração cherry-picked      [enganoso]

NOTE: All charts use df_clean (cleaned data), not the raw CSV.
Run: python imdb_viz.py
"""
from __future__ import annotations
import os, random, warnings
import tkinter as tk
import pandas as pd
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
warnings.filterwarnings("ignore")

try:
    import mplcursors
    _CURSORS = True
except ImportError:
    _CURSORS = False

PLOTS_DIR = "plots"
os.makedirs(PLOTS_DIR, exist_ok=True)

# ── palette ───────────────────────────────────────────────────────────────────
DARK   = "#0e0e12"
SURF   = "#16161c"
BORDER = "#2a2a35"
TEXT   = "#e8e6e0"
MUTED  = "#6b6878"
ACCENT = "#f5c842"
RED    = "#e84c2b"
GREEN  = "#3dd68c"
GENRE_COLORS = [
    "#f5c842","#e84c2b","#3dd68c","#5b9cf6",
    "#b57aff","#ff8c42","#42d9ff","#ff42a1",
]

CHART_REGISTRY = [
    ("C1", "Rating por Género",        "correto",   GREEN),
    ("C2", "Filmes por Década",        "correto",   GREEN),
    ("E1", "Revenue por Género",       "enganoso",  RED),
    ("E2", "Duração — Cherry-picking", "enganoso",  RED),
]

import matplotlib.pyplot as plt
plt.rcParams.update({
    "figure.facecolor": DARK, "axes.facecolor": SURF,
    "axes.edgecolor": BORDER, "axes.labelcolor": TEXT,
    "xtick.color": TEXT, "ytick.color": TEXT, "text.color": TEXT,
    "grid.color": BORDER, "grid.linewidth": 0.5,
})

# ── data ──────────────────────────────────────────────────────────────────────
def load_and_clean(filepath: str = "imdb_top_1000.csv") -> pd.DataFrame:
    """Load CSV and return df_clean with corrected dtypes.

    Cleaning applied (same logic as imdb_analysis.py):
      - encoding='latin-1'  (CSV has Léon etc.)
      - Released_Year='PG'  → 1 scraping-error row dropped
      - Runtime             → strip ' min', cast Int64
      - Gross               → strip '$' and ',', cast Float64 (NaN kept)
      - Primary_Genre       → first genre listed
      - Decade              → Year floored to decade
    """
    try:
        df_raw = pd.read_csv(filepath, encoding="latin-1")
    except FileNotFoundError:
        import tkinter.messagebox as mb
        mb.showerror("Ficheiro não encontrado",
                     f"'{filepath}' não encontrado.\n"
                     "Coloca imdb_top_1000.csv na mesma pasta.")
        raise SystemExit(1)

    raw_rows = len(df_raw)
    df = df_raw.copy()

    df["Year"] = pd.to_numeric(df["Released_Year"], errors="coerce")
    bad = int(df["Year"].isna().sum())
    df  = df[df["Year"].notna()].copy()
    df["Year"] = df["Year"].astype(int)

    df["Runtime_min"] = pd.to_numeric(
        df["Runtime"].astype(str).str.replace(" min","",regex=False).str.strip(),
        errors="coerce").astype("Int64")

    df["Gross_num"] = pd.to_numeric(
        df["Gross"].astype(str)
          .str.replace("$","",regex=False).str.replace(",","",regex=False)
          .str.strip().replace({"nan": pd.NA,"": pd.NA}),
        errors="coerce").astype("Float64")

    df["Primary_Genre"] = df["Genre"].astype(str).str.split(",").str[0].str.strip()
    df["Decade"]        = (df["Year"] // 10 * 10).astype(int)

    print("─" * 55)
    print("df_clean  (imdb_viz.py usa dados já tratados)")
    print(f"  CSV original          : {raw_rows} linhas")
    print(f"  Removidas (Year='PG') : {bad}")
    print(f"  df_clean              : {len(df)} linhas")
    print(f"  Runtime_min           : {df['Runtime_min'].dtype}")
    print(f"  Gross_num             : {df['Gross_num'].dtype}  "
          f"({int(df['Gross_num'].isna().sum())} NaN mantidos)")
    print("─" * 55)
    return df


def top_genres(df: pd.DataFrame, n: int = 8) -> list[str]:
    """Return the n most frequent primary genres."""
    return df["Primary_Genre"].value_counts().head(n).index.tolist()


def _style_ax(ax) -> None:
    """Apply dark theme to axes."""
    ax.set_facecolor(SURF)
    for sp in ax.spines.values():
        sp.set_edgecolor(BORDER)
    ax.tick_params(colors=TEXT, labelsize=8)
    ax.xaxis.label.set_color(TEXT)
    ax.yaxis.label.set_color(TEXT)


def _watermark(fig, label: str, color: str) -> None:
    """Add a tiny discrete label in the bottom-left corner — crop-safe."""
    fig.text(0.005, 0.004, label,
             ha="left", va="bottom",
             color=color, fontsize=5.5, alpha=0.35,
             fontfamily="monospace")


# ── chart builders ────────────────────────────────────────────────────────────

def build_C1(df: pd.DataFrame, fig: Figure) -> None:
    """C1 — IMDB Rating distribution per genre. CORRECT."""
    fig.clear()
    fig.patch.set_facecolor(DARK)
    ax = fig.add_subplot(111)
    _style_ax(ax)

    genres = top_genres(df)
    data   = [df.loc[df["Primary_Genre"]==g,"IMDB_Rating"].dropna().values for g in genres]

    parts = ax.violinplot(data, positions=range(len(genres)),
                          showmedians=True, showextrema=False)
    for pc, c in zip(parts["bodies"], GENRE_COLORS):
        pc.set_facecolor(c); pc.set_alpha(0.5); pc.set_edgecolor("none")
    parts["cmedians"].set_color("#ffffff"); parts["cmedians"].set_linewidth(1.8)

    rng = random.Random(42)
    for i, (vals, c) in enumerate(zip(data, GENRE_COLORS)):
        j = [i + rng.uniform(-0.18, 0.18) for _ in vals]
        ax.scatter(j, vals, s=11, color=c, alpha=0.6, zorder=3, edgecolors="none")

    ax.set_xticks(range(len(genres)))
    ax.set_xticklabels(genres, rotation=30, ha="right")
    ax.set_ylabel("IMDB Rating")
    ax.set_ylim(7.4, 9.5)
    ax.yaxis.grid(True, linestyle="--"); ax.set_axisbelow(True)
    ax.set_title("Distribuição de Rating IMDB por Género", color=TEXT, fontweight="bold")

    if _CURSORS:
        mplcursors.cursor(ax.collections, hover=True)

    _watermark(fig, "C1 · correto · eixo Y = 7.4 (mín real Top 1000, declarado) · cada ponto = 1 filme · linha branca = mediana", GREEN)
    fig.tight_layout(rect=[0, 0.02, 1, 1])
    fig.savefig(f"{PLOTS_DIR}/C1_rating_by_genre.png", dpi=150, bbox_inches="tight")


def build_C2(df: pd.DataFrame, fig: Figure) -> None:
    """C2 — Films per decade. CORRECT."""
    fig.clear()
    fig.patch.set_facecolor(DARK)
    ax = fig.add_subplot(111)
    _style_ax(ax)

    counts = df[df["Decade"] >= 1920]["Decade"].value_counts().sort_index()
    bars = ax.bar(counts.index.astype(str), counts.values,
                  color=GENRE_COLORS[:len(counts)], width=0.6, edgecolor=DARK, linewidth=0.8)
    ax.set_ylim(0, counts.max() * 1.15)
    ax.set_ylabel("Nº de filmes no Top 1000")
    ax.yaxis.grid(True, linestyle="--"); ax.set_axisbelow(True)
    for bar, v in zip(bars, counts.values):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+2,
                str(v), ha="center", va="bottom", fontsize=8)
    ax.set_title("Filmes do Top 1000 IMDB por Década", color=TEXT, fontweight="bold")

    _watermark(fig, "C2 · correto · eixo Y começa em 0 · sem manipulação de escala", GREEN)
    fig.tight_layout(rect=[0, 0.02, 1, 1])
    fig.savefig(f"{PLOTS_DIR}/C2_films_per_decade.png", dpi=150, bbox_inches="tight")


def build_E1(df: pd.DataFrame, fig: Figure) -> None:
    """E1 — Mean revenue by genre. MISLEADING: truncated Y, mean, silent NaN exclusion, no budget normalisation."""
    fig.clear()
    fig.patch.set_facecolor(DARK)
    ax = fig.add_subplot(111)
    _style_ax(ax)

    genre_gross = (df.groupby("Primary_Genre")["Gross_num"]
                   .mean().dropna().sort_values(ascending=False).head(8))
    genres = genre_gross.index.tolist()
    means  = (genre_gross.values / 1e6).tolist()

    bars = ax.bar(genres, means, color=GENRE_COLORS[:len(genres)],
                  width=0.6, edgecolor=DARK, linewidth=0.8)
    ax.set_ylim(min(means) * 0.80, max(means) * 1.1)   # ← TRUNCATED
    ax.set_xticklabels(genres, rotation=30, ha="right")
    ax.set_ylabel("Revenue médio ($ milhões)")
    ax.yaxis.grid(True, linestyle="--"); ax.set_axisbelow(True)
    for bar, v in zip(bars, means):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.5,
                f"${v:.0f}M", ha="center", va="bottom", fontsize=7.5, fontweight="bold")
    ax.set_title("Revenue Médio por Género (IMDB Top 1000)", color=TEXT, fontweight="bold")

    _watermark(fig,
               "E1 · enganoso · ① eixo Y truncado  ② média não mediana  "
               "③ 169 filmes sem Gross excluídos  ④ sem normalização de orçamento",
               RED)
    fig.tight_layout(rect=[0, 0.02, 1, 1])
    fig.savefig(f"{PLOTS_DIR}/E1_misleading_revenue.png", dpi=150, bbox_inches="tight")


def build_E2(df: pd.DataFrame, fig: Figure) -> None:
    """E2 — Runtime trend. MISLEADING: cherry-picked decade range shown as 'growing trend'."""
    fig.clear()
    fig.patch.set_facecolor(DARK)

    runtime_dec    = df.groupby("Decade")["Runtime_min"].median().dropna()
    runtime_full   = runtime_dec[runtime_dec.index >= 1960]
    runtime_cherry = runtime_dec[(runtime_dec.index >= 1980) & (runtime_dec.index <= 2019)]

    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122, sharey=ax1)

    for ax, data, title in [
        (ax1, runtime_full,   "Duração Mediana — série completa (1960–2020)"),
        (ax2, runtime_cherry, "Duração Mediana — tendência crescente"),
    ]:
        color = GREEN if ax is ax1 else RED
        _style_ax(ax)
        ax.plot(data.index, data.values,
                marker="o", color=color, linewidth=2.2, markersize=6,
                markerfacecolor=DARK, markeredgecolor=color, markeredgewidth=2)
        ax.set_xticks(data.index)
        ax.set_xticklabels([str(x)+"s" for x in data.index], rotation=30, ha="right")
        ax.set_ylim(90, 148)
        ax.yaxis.grid(True, linestyle="--"); ax.set_axisbelow(True)
        ax.set_xlabel("Década"); ax.set_ylabel("Duração mediana (min)")
        ax.set_title(title, color=TEXT, fontweight="bold", fontsize=9)

    fig.suptitle("Duração Mediana dos Filmes por Década", color=TEXT, fontweight="bold")
    _watermark(fig,
               "E2 · enganoso · gráfico direita: cherry-picking (1980–2019) esconde estabilização das décadas anteriores",
               RED)
    fig.tight_layout()
    fig.savefig(f"{PLOTS_DIR}/E2_misleading_runtime_cherry.png", dpi=150, bbox_inches="tight")


BUILDERS: dict[str, object] = {
    "C1": build_C1, "C2": build_C2, "E1": build_E1, "E2": build_E2
}


# ── app ───────────────────────────────────────────────────────────────────────
class App(tk.Tk):
    """Main Tkinter window."""

    def __init__(self) -> None:
        super().__init__()
        self.title("IMDB Top 1000 · Visualizações · IACD DV T2")
        self.configure(bg=DARK)
        self.geometry("1060x700")
        self.df = load_and_clean()

        # header
        bar = tk.Frame(self, bg=DARK, padx=12, pady=7)
        bar.pack(fill="x")
        tk.Label(bar, text="IMDB Top 1000",
                 font=("Courier", 13, "bold"), bg=DARK, fg=ACCENT).pack(side="left")
        tk.Label(bar, text="  ·  IACD Visualização de Dados  ·  UBI",
                 font=("Courier", 8), bg=DARK, fg=MUTED).pack(side="left")

        # clean-data badge
        tk.Label(bar,
                 text=f"  df_clean: {len(self.df)} linhas · Runtime Int · Gross Float",
                 font=("Courier", 7), bg=DARK, fg=GREEN).pack(side="right", padx=8)

        # radio buttons
        btn_frame = tk.Frame(self, bg=DARK, padx=12, pady=4)
        btn_frame.pack(fill="x")
        tk.Label(btn_frame, text="Gráfico:", font=("Courier", 8),
                 bg=DARK, fg=MUTED).pack(side="left", padx=(0, 8))
        self._chart = tk.StringVar(value="C1")
        for code, label, kind, color in CHART_REGISTRY:
            tk.Radiobutton(
                btn_frame,
                text=f"  {code} — {label}  [{kind}]  ",
                variable=self._chart, value=code,
                font=("Courier", 8), bg=DARK, fg=color,
                activebackground=SURF, activeforeground=color,
                selectcolor=SURF, indicatoron=True,
                command=self._draw,
            ).pack(side="left", padx=4)

        # figure
        self._fig = Figure(figsize=(10, 5.8), dpi=100, facecolor=DARK)
        canvas = FigureCanvasTkAgg(self._fig, master=self)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        self._canvas = canvas

        # toolbar
        tb = tk.Frame(self, bg=DARK)
        tb.pack(fill="x", side="bottom")
        NavigationToolbar2Tk(canvas, tb).update()

        # status bar
        self._status = tk.StringVar()
        tk.Label(self, textvariable=self._status,
                 font=("Courier", 7), bg=SURF, fg=MUTED,
                 anchor="w", padx=8, pady=3).pack(fill="x", side="bottom")

        self._draw()

    def _draw(self) -> None:
        key = self._chart.get()
        BUILDERS[key](self.df, self._fig)
        self._canvas.draw()
        _, label, kind, color = next(r for r in CHART_REGISTRY if r[0] == key)
        self._status.set(
            f"{key} — {label}  [{kind}]  |  Guardado: {PLOTS_DIR}/{key}_*.png  "
            f"|  Dados: df_clean (999 linhas, tipos corrigidos)"
        )


def main() -> None:
    App().mainloop()


if __name__ == "__main__":
    main()