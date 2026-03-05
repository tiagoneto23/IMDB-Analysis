"""IMDB Top 1000 dataset inspection and quality diagnostics."""

from __future__ import annotations

import pandas as pd


def print_section(title: str) -> None:
    """Print a readable terminal section header."""
    print(f"\n{'=' * 60}")
    print(title)
    print("=" * 60)


def warn_missing_expected_columns(df: pd.DataFrame) -> list[str]:
    """Warn if expected columns are missing and return them."""
    expected_columns = [
        "Series_Title",
        "IMDB_Rating",
        "Gross",
        "Meta_score",
        "Runtime",
        "Released_Year",
        "Genre",
        "Certificate",
    ]
    missing_columns = [col for col in expected_columns if col not in df.columns]
    if missing_columns:
        print(
            "WARNING: Missing expected columns: "
            + ", ".join(missing_columns)
        )
    return missing_columns


def load_data(filepath: str) -> pd.DataFrame:
    """Load CSV data and print basic structure details."""
    try:
        # encoding="latin-1" is required: the IMDB CSV contains non-UTF-8
        # characters (e.g. "Léon: The Professional") that crash the default
        # utf-8 decoder with UnicodeDecodeError.
        df = pd.read_csv(filepath, encoding="latin-1")
    except FileNotFoundError:
        print_section("LOAD DATA")
        print(f"ERROR: File not found -> {filepath}")
        return pd.DataFrame()
    except UnicodeDecodeError as exc:
        print_section("LOAD DATA")
        print(f"ERROR: Encoding mismatch reading {filepath}: {exc}")
        print("Try opening the file in a text editor and saving as UTF-8.")
        return pd.DataFrame()

    print_section("LOAD DATA")
    print(f"Dataset shape: {df.shape[0]} rows x {df.shape[1]} columns")
    print("\nData types:")
    print(df.dtypes.to_string())
    print("\nFirst 5 rows:")
    print(df.head(5).to_string(index=False))
    return df


def inspect_columns(df: pd.DataFrame) -> None:
    """Inspect schema, object values, and semantic type mismatches."""
    print("Columns and dtypes:")
    schema_df = pd.DataFrame(
        {
            "column": df.columns,
            "dtype": df.dtypes.astype(str).values,
        }
    )
    print(schema_df.to_string(index=False))

    object_columns = df.select_dtypes(include=["object"]).columns.tolist()
    if object_columns:
        print("\nTop 5 value counts for object columns (including NaN):")
        for col in object_columns:
            print(f"\n- {col}:")
            print(df[col].value_counts(dropna=False).head(5).to_string())
    else:
        print("\nNo object columns found.")

    expected_numeric_columns = [
        "Released_Year",
        "Runtime",
        "IMDB_Rating",
        "Meta_score",
        "No_of_Votes",
        "Gross",
    ]
    mismatches = [
        col
        for col in expected_numeric_columns
        if col in df.columns and not pd.api.types.is_numeric_dtype(df[col])
    ]
    if mismatches:
        print("\nSemantic dtype mismatches (expected numeric but current dtype is not):")
        for col in mismatches:
            print(f"- {col}: {df[col].dtype}")
    else:
        print("\nNo semantic dtype mismatches detected for expected numeric columns.")

    print("\nKnown data issue checks:")

    if "Released_Year" in df.columns:
        released_year_raw = df["Released_Year"].copy()
        released_year_num = pd.to_numeric(released_year_raw, errors="coerce")
        bad_year_mask = released_year_num.isna() & released_year_raw.notna()
        bad_year_count = int(bad_year_mask.sum())
        print(f"- Released_Year coercion (errors='coerce') produced NaN in {bad_year_count} rows.")
        if bad_year_count > 0:
            print("  Original bad Released_Year values:")
            print(released_year_raw[bad_year_mask].astype(str).value_counts().to_string())
            cols_to_show = ["Released_Year"]
            if "Series_Title" in df.columns:
                cols_to_show.insert(0, "Series_Title")
            print("  Sample affected rows:")
            print(df.loc[bad_year_mask, cols_to_show].head(10).to_string(index=False))
            released_year_clean = released_year_num[~bad_year_mask].astype("Int64")
            print(
                "  Rows remaining after dropping invalid Released_Year on a copy: "
                f"{released_year_clean.shape[0]}"
            )
    else:
        print("- Released_Year column not found.")

    if "Runtime" in df.columns:
        runtime_raw = df["Runtime"].copy()
        runtime_clean = runtime_raw.astype(str).str.replace(" min", "", regex=False).str.strip()
        runtime_clean = runtime_clean.where(runtime_raw.notna(), pd.NA)
        runtime_num = pd.to_numeric(runtime_clean, errors="coerce").astype("Int64")
        runtime_bad_mask = runtime_num.isna() & runtime_raw.notna()
        print(
            "- Runtime cleaned by stripping ' min' then casting to int (nullable Int64). "
            f"Invalid runtime rows after conversion: {int(runtime_bad_mask.sum())}."
        )
        if int(runtime_bad_mask.sum()) > 0:
            print("  Bad Runtime values (top 5):")
            print(runtime_raw[runtime_bad_mask].astype(str).value_counts().head(5).to_string())
    else:
        print("- Runtime column not found.")

    if "Gross" in df.columns:
        gross_raw = df["Gross"].copy()
        gross_clean = (
            gross_raw.astype(str)
            .str.replace("$", "", regex=False)
            .str.replace(",", "", regex=False)
            .str.strip()
        )
        gross_clean = gross_clean.replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})
        gross_num = pd.to_numeric(gross_clean, errors="coerce").astype("Float64")
        gross_bad_mask = gross_num.isna() & gross_raw.notna()
        print(
            "- Gross cleaned by removing '$' and commas, then cast to float. "
            f"Invalid non-null Gross rows after conversion: {int(gross_bad_mask.sum())}."
        )
        if int(gross_bad_mask.sum()) > 0:
            print("  Bad Gross values (top 5):")
            print(gross_raw[gross_bad_mask].astype(str).value_counts().head(5).to_string())
    else:
        print("- Gross column not found.")

    if "Meta_score" in df.columns:
        meta_missing = int(df["Meta_score"].isna().sum())
        print(f"- Meta_score missing values (reported only, not dropped): {meta_missing}.")
    else:
        print("- Meta_score column not found.")

    if "Certificate" in df.columns:
        certificate = df["Certificate"].copy()
        certificate_missing = int(certificate.isna().sum())
        certificate_non_null = certificate.dropna().astype(str).str.strip()
        print(f"- Certificate missing values: {certificate_missing}.")
        print("  Certificate top values:")
        print(certificate_non_null.value_counts().head(10).to_string())

        us_ratings = {
            "G",
            "PG",
            "PG-13",
            "R",
            "NC-17",
            "TV-14",
            "TV-MA",
            "TV-PG",
            "TV-G",
            "Approved",
            "Passed",
            "Unrated",
            "Not Rated",
            "GP",
        }
        indian_ratings = {"U", "UA", "A", "S", "U/A"}
        present_values = set(certificate_non_null.unique())
        present_us = sorted(present_values.intersection(us_ratings))
        present_indian = sorted(present_values.intersection(indian_ratings))
        if present_us and present_indian:
            print(
                "  WARNING: Mixed certificate systems detected "
                f"(US: {present_us}; Indian: {present_indian})."
            )
    else:
        print("- Certificate column not found.")


def analyze_missing(df: pd.DataFrame) -> pd.DataFrame:
    """Return and print a missing-values summary table."""
    missing_count = df.isna().sum()
    missing_pct = (df.isna().mean() * 100).round(2)
    summary = pd.DataFrame(
        {
            "column": missing_count.index,
            "missing_count": missing_count.values,
            "missing_pct": missing_pct.values,
        }
    ).sort_values("missing_pct", ascending=False, ignore_index=True)

    missing_only = summary[summary["missing_pct"] > 0]
    if missing_only.empty:
        print("No missing values found in any column.")
    else:
        print("Columns with missing_pct > 0 (sorted descending):")
        print(missing_only.to_string(index=False))
    return summary


def analyze_duplicates(df: pd.DataFrame) -> None:
    """Report exact duplicates and possible title-level duplicates."""
    exact_duplicate_count = int(df.duplicated().sum())
    print(f"Exact duplicate rows: {exact_duplicate_count}")
    if exact_duplicate_count > 0:
        print("Examples of exact duplicates:")
        print(df[df.duplicated(keep=False)].head(10).to_string(index=False))

    if "Series_Title" not in df.columns:
        print("WARNING: Series_Title column missing; cannot check title duplicates.")
        return

    title_duplicate_count = int(df["Series_Title"].duplicated().sum())
    print(f"Duplicate Series_Title values: {title_duplicate_count}")
    if title_duplicate_count > 0:
        cols_to_show = [
            col
            for col in ["Series_Title", "Released_Year", "Director", "Certificate"]
            if col in df.columns
        ]
        print("Examples of title duplicates:")
        print(
            df.loc[df["Series_Title"].duplicated(keep=False), cols_to_show]
            .head(10)
            .to_string(index=False)
        )


def main() -> None:
    """Run the complete IMDB data inspection workflow."""
    print_section("IMDB TOP 1000 DATA QUALITY ANALYSIS")
    filepath = "imdb_top_1000.csv"

    df = load_data(filepath)
    if df.empty:
        print("No data loaded. Exiting.")
        return

    warn_missing_expected_columns(df)

    print_section("COLUMN INSPECTION")
    inspect_columns(df)

    print_section("MISSING VALUE ANALYSIS")
    missing_summary = analyze_missing(df)

    print_section("DUPLICATE ANALYSIS")
    analyze_duplicates(df)

    rows, columns = df.shape
    columns_with_missing = int((missing_summary["missing_count"] > 0).sum())
    exact_duplicate_count = int(df.duplicated().sum())
    title_duplicate_count = (
        int(df["Series_Title"].duplicated().sum())
        if "Series_Title" in df.columns
        else 0
    )

    print_section("FINAL SUMMARY")
    print(
        "SUMMARY: "
        f"{rows} rows, {columns} columns. "
        f"{columns_with_missing} columns with missing data. "
        f"{exact_duplicate_count} exact duplicates. "
        f"{title_duplicate_count} title duplicates."
    )


if __name__ == "__main__":
    main()