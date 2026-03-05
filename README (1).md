# IMDB Top 1000 — Data Visualization Assignment
**IACD · Visualização de Dados · Tarefa 2 · UBI 2024/25**

---

## Dataset

**IMDB Dataset of Top 1000 Movies and TV Shows**
→ https://www.kaggle.com/datasets/harshitshankhdhar/imdb-dataset-of-top-1000-movies-and-tv-shows

Download `imdb_top_1000.csv` and place it in this folder.

---

## Project structure

```
.
├── imdb_top_1000.csv       ← dataset from Kaggle (not committed)
├── imdb_analysis.py        ← Tarefa 2 · pontos 1 e 2  (data inspection)
├── imdb_viz.py             ← Tarefa 2 · pontos 3 e 4  (visualizations)
├── requirements.txt
└── README.md
```

---

## Setup

```bash
# 1. Create and activate a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# Linux only — if tkinter is not found:
# sudo apt-get install python3-tk
```

---

## Usage

### Pontos 1 & 2 — Load and inspect data

```bash
python imdb_analysis.py
```

Prints to terminal:
- Dataset shape, dtypes, first 5 rows
- Column inspection with semantic dtype mismatch detection
- Known data issues explicitly checked:
  - `Released_Year` has a `"PG"` scraping error
  - `Runtime` stored as `"142 min"` (string, not int)
  - `Gross` stored as `"$28,341,469"` (string with $ and commas)
  - `Meta_score` has ~157 NaN (reported, not dropped)
  - `Certificate` has mixed US and Indian rating systems
- Missing values per column (count + %)
- Exact and title-level duplicate detection
- Final summary line

### Pontos 3 & 4 — Interactive visualizations

```bash
python imdb_viz.py
```

Opens a Tkinter window with:
- **Dropdown** to switch between charts
- **Correct chart** — IMDB Rating Distribution by Genre (violin + strip plot)
- **Misleading chart** — Average Gross Revenue by Genre (truncated axis, mean skewed by blockbusters)
- Built-in **zoom / pan / save** toolbar (matplotlib NavigationToolbar)
- **Hover tooltips** on data points (requires `mplcursors`)

---

## Known data issues (documented)

| Column | Issue | Handled in |
|---|---|---|
| `Released_Year` | Contains `"PG"` (scraping error) | `imdb_analysis.py` line 96 |
| `Runtime` | String `"142 min"` instead of int | `imdb_analysis.py` line 118 |
| `Gross` | String with `$` and `,` | `imdb_analysis.py` line 134 |
| `Meta_score` | ~157 NaN (~15.7%) | reported only, not dropped |
| `Certificate` | ~100 NaN + mixed US/Indian systems | `imdb_analysis.py` line 161 |
| Encoding | File uses `latin-1` (e.g. `Léon`) | `pd.read_csv(..., encoding="latin-1")` |

---

## Why the misleading chart misleads

1. **Truncated Y-axis** — differences look 3–5× larger than they are
2. **Mean, not median** — skewed by billion-dollar blockbusters
3. **~170 films with no `Gross` data silently excluded** — selection bias
4. **No budget normalisation** — Action films cost 5–10× more to produce; ROI may be lower than Drama

This is intentional for point 4 of the assignment: the chart is meant to look convincing while being technically dishonest.