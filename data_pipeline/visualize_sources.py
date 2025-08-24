# visualize_sources.py
import os
import argparse
import logging

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def _abs_path(*parts) -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, *parts)


def load_presence_df(csv_path: str) -> pd.DataFrame:
    """
    Load the presence matrix CSV with columns: vendor, yelp, foursquare, osm.
    """
    df = pd.read_csv(csv_path)
    expected = {"vendor", "yelp", "foursquare", "osm"}
    missing = expected - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing expected columns: {missing}")
    return df


def plot_unique_counts(df: pd.DataFrame, out_path: str) -> None:
    """
    Bar chart of unique vendor coverage per source (count of groups where source==1).
    """
    counts = {
        "OSM": int(df["osm"].sum()),
        "Yelp": int(df["yelp"].sum()),
        "Foursquare": int(df["foursquare"].sum()),
    }
    sns.set(style="whitegrid")
    plt.figure(figsize=(6, 4))
    ax = sns.barplot(x=list(counts.keys()), y=list(counts.values()), palette="Set2")
    ax.set_title("Unique vendors per source")
    ax.set_ylabel("Count of unique vendors")
    ax.set_xlabel("")
    for p in ax.patches:
        ax.annotate(
            f"{int(p.get_height())}",
            (p.get_x() + p.get_width() / 2, p.get_height()),
            ha="center", va="bottom", fontsize=10, xytext=(0, 3), textcoords="offset points"
        )
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    logger.info(f"Saved bar chart -> {out_path}")


def compute_overlap_matrices(df: pd.DataFrame):
    """
    Compute pairwise overlap matrices (counts and Jaccard similarity) for sources.
    Returns:
      labels: list of source labels
      counts: 3x3 numpy array (diagonal=source totals, off-diagonal=overlap counts)
      jaccard: 3x3 numpy array with Jaccard similarities
    """
    labels = ["OSM", "Yelp", "Foursquare"]
    cols = {"OSM": "osm", "Yelp": "yelp", "Foursquare": "foursquare"}

    # Totals per source (diagonal)
    totals = {k: int(df[cols[k]].sum()) for k in labels}

    # Overlap counts
    overlaps = np.zeros((3, 3), dtype=int)
    for i, a in enumerate(labels):
        for j, b in enumerate(labels):
            if i == j:
                overlaps[i, j] = totals[a]
            else:
                overlaps[i, j] = int(((df[cols[a]] == 1) & (df[cols[b]] == 1)).sum())

    # Jaccard = |A ∩ B| / |A ∪ B|
    jaccard = np.zeros((3, 3), dtype=float)
    for i, a in enumerate(labels):
        for j, b in enumerate(labels):
            inter = overlaps[i, j] if i != j else totals[a]
            union = totals[a] + totals[b] - (overlaps[i, j] if i != j else totals[a])
            if union == 0:
                jaccard[i, j] = 0.0
            else:
                jaccard[i, j] = inter / union if i != j else 1.0

    return labels, overlaps, jaccard


def plot_heatmap(matrix: np.ndarray, labels, title: str, out_path: str, fmt: str = "d", cmap: str = "YlGnBu"):
    """
    Generic annotated heatmap plotter.
    """
    sns.set(style="white")
    plt.figure(figsize=(6, 5))
    ax = sns.heatmap(
        matrix,
        annot=True,
        fmt=fmt,
        xticklabels=labels,
        yticklabels=labels,
        cmap=cmap,
        cbar=True,
        linewidths=0.5,
        linecolor="white",
        square=True,
    )
    ax.set_title(title)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    logger.info(f"Saved heatmap -> {out_path}")


def visualize(csv_path: str = None):
    """
    Load presence matrix CSV and generate:
      - Bar chart of unique counts per source
      - Heatmap of overlap counts
      - Heatmap of Jaccard similarity
    """
    if not csv_path:
        csv_path = _abs_path("outputs", "sources_comparison.csv")

    df = load_presence_df(csv_path)

    # Prepare output directory (same folder as CSV)
    out_dir = os.path.dirname(os.path.abspath(csv_path))
    os.makedirs(out_dir, exist_ok=True)

    # Plots
    plot_unique_counts(df, os.path.join(out_dir, "unique_counts_bar.png"))

    labels, counts, jaccard = compute_overlap_matrices(df)
    plot_heatmap(counts, labels, "Overlap counts by source", os.path.join(out_dir, "overlap_heatmap_counts.png"), fmt="d")
    plot_heatmap(jaccard, labels, "Jaccard similarity by source", os.path.join(out_dir, "overlap_heatmap_jaccard.png"), fmt=".2f", cmap="BuPu")


def main():
    parser = argparse.ArgumentParser(description="Visualize vendor source coverage and overlaps.")
    parser.add_argument("--csv", default=None, help="Path to sources_comparison.csv (defaults to sources/sources_comparison.csv)")
    args = parser.parse_args()
    visualize(args.csv)


if __name__ == "__main__":
    main()