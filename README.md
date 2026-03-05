[README (1).md](https://github.com/user-attachments/files/25775608/README.1.md)
<div align="center">

# 🎬 IMDB Top 1000 — Data Visualization

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-2.0%2B-150458?style=flat-square&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Matplotlib](https://img.shields.io/badge/Matplotlib-3.7%2B-11557c?style=flat-square)](https://matplotlib.org/)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)](LICENSE)
[![UBI](https://img.shields.io/badge/UBI-IACD%202024%2F25-f5c842?style=flat-square)](https://www.ubi.pt)

**IACD · Visualização de Dados · Tarefa 2**

*Análise de qualidade de dados + visualizações corretas e enganosas sobre o dataset IMDB Top 1000*

</div>

---

## ✨ Highlights

| | |
|---|---|
| 📊 **4 charts** | 2 corretos · 2 deliberadamente enganosos |
| 🧹 **Data cleaning** | Runtime, Gross, Year — tipos corrigidos, erros documentados |
| 🖥️ **Interactive UI** | Tkinter com zoom, pan e export PNG |
| 🔍 **Full audit trail** | Cada manipulação identificada e explicada |

---

## 📁 Structure

```
.
├── imdb_top_1000.csv        ← dataset (Kaggle, não versionado)
├── imdb_analysis.py         ← Pontos 1 & 2 · inspeção e qualidade de dados
├── imdb_viz.py              ← Pontos 3 & 4 · visualizações interativas
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

```bash
# 1. Clone & setup
git clone https://github.com/<user>/<repo>.git && cd <repo>
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt
# Linux only: sudo apt-get install python3-tk

# 3. Download dataset → https://www.kaggle.com/datasets/harshitshankhdhar/imdb-dataset-of-top-1000-movies-and-tv-shows
#    Place imdb_top_1000.csv in the project root

# 4. Run
python imdb_analysis.py   # data inspection (terminal)
python imdb_viz.py        # interactive charts (GUI)
```

---

## 📊 Charts

### ✅ Correct

| ID | Chart | Why it's honest |
|----|-------|-----------------|
| **C1** | Rating Distribution by Genre | Y-axis starts at real minimum · median shown · every point = 1 film |
| **C2** | Films per Decade | Y-axis from 0 · no scale manipulation · raw counts labelled |

### ⚠️ Misleading (intentional — assignment point 4)

| ID | Chart | Manipulation |
|----|-------|--------------|
| **E1** | Average Revenue by Genre | ① Truncated Y-axis · ② mean instead of median · ③ 169 films silently excluded · ④ no budget normalisation |
| **E2** | Median Runtime Trend | Cherry-picked 1980–2019 window hides the flat trend visible in the full 1960–2020 series |

---

## 🧹 Known Data Issues

| Column | Issue | Fix |
|--------|-------|-----|
| `Released_Year` | `"PG"` scraping error (1 row) | Dropped after `pd.to_numeric(errors='coerce')` |
| `Runtime` | Stored as `"142 min"` string | Strip `" min"` → cast `Int64` |
| `Gross` | Stored as `"$28,341,469"` string | Strip `$` and `,` → cast `Float64` (NaN kept) |
| `Meta_score` | ~157 NaN (~15.7%) | Reported only, not dropped |
| `Certificate` | Mixed US + Indian systems | Documented, flagged in output |
| Encoding | `latin-1` chars (e.g. *Léon*) | `pd.read_csv(..., encoding='latin-1')` |

---

## 🛠️ Tech Stack

`Python 3.10+` · `pandas` · `matplotlib` · `tkinter` · `mplcursors`

---

<div align="center">
  <sub>Made with ☕ · UBI · IACD 2024/25</sub>
</div>
