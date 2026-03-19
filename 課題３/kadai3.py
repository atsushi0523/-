from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def _set_japanese_font() -> None:
    # 実行環境により日本語フォントが異なるため、候補を複数指定
    plt.rcParams["font.family"] = [
        "Meiryo",
        "Yu Gothic",
        "MS Gothic",
        "Noto Sans CJK JP",
        "IPAexGothic",
        "DejaVu Sans",
    ]
    plt.rcParams["axes.unicode_minus"] = False


def main() -> None:
    here = Path(__file__).resolve().parent
    csv_path = here / "課題3.csv"

    df = pd.read_csv(csv_path)

    if not {"名前", "所属", "スコア"}.issubset(df.columns):
        raise ValueError("CSVの列名は「名前」「所属」「スコア」である必要があります。")

    _set_japanese_font()

    # 1) 円グラフ: 所属ごとの参加者数（割合）
    counts = df["所属"].value_counts().sort_index()
    fig1, ax1 = plt.subplots(figsize=(7, 7))
    ax1.pie(
        counts.values,
        labels=counts.index,
        autopct="%1.1f%%",
        startangle=90,
        counterclock=False,
        textprops={"fontsize": 11},
    )
    ax1.set_title("所属ごとの参加者割合", fontsize=14)
    ax1.axis("equal")
    fig1.tight_layout()
    fig1.savefig(here / "pie_shozoku.png", dpi=200)
    plt.close(fig1)

    # 2) 棒グラフ: 所属ごとの平均スコア
    avg_by_dept = df.groupby("所属")["スコア"].mean().sort_index()
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    ax2.bar(avg_by_dept.index, avg_by_dept.values, color="#4C78A8")
    ax2.set_title("所属ごとの平均スコア", fontsize=14)
    ax2.set_xlabel("所属")
    ax2.set_ylabel("平均スコア")
    ax2.grid(axis="y", linestyle="--", alpha=0.4)
    for x, v in zip(avg_by_dept.index, avg_by_dept.values):
        ax2.text(x, v, f"{v:.1f}", ha="center", va="bottom", fontsize=10)
    fig2.tight_layout()
    fig2.savefig(here / "bar_avg_score_by_shozoku.png", dpi=200)
    plt.close(fig2)

    # 3) ヒストグラム: スコア分布
    scores = pd.to_numeric(df["スコア"], errors="coerce").dropna()
    fig3, ax3 = plt.subplots(figsize=(8, 5))
    ax3.hist(scores, bins=10, color="#F58518", edgecolor="white")
    ax3.set_title("全参加者のスコア分布", fontsize=14)
    ax3.set_xlabel("スコア")
    ax3.set_ylabel("人数")
    ax3.grid(axis="y", linestyle="--", alpha=0.4)
    fig3.tight_layout()
    fig3.savefig(here / "hist_score.png", dpi=200)
    plt.close(fig3)

    print("保存しました:")
    print(f"- {csv_path.name}")
    print(f"- pie_shozoku.png")
    print(f"- bar_avg_score_by_shozoku.png")
    print(f"- hist_score.png")


if __name__ == "__main__":
    main()
