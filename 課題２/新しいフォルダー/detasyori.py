from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
import sys


@dataclass(frozen=True)
class Stats:
    count: int
    avg: float
    max_: int
    min_: int


def calc_stats(scores: list[int]) -> Stats:
    if not scores:
        raise ValueError("scores is empty")
    return Stats(
        count=len(scores),
        avg=sum(scores) / len(scores),
        max_=max(scores),
        min_=min(scores),
    )


def read_scores_by_person(csv_path: Path) -> dict[str, list[int]]:
    scores_by_person: dict[str, list[int]] = {}
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("CSVヘッダーが見つかりません")
        if "名前" not in reader.fieldnames or "スコア" not in reader.fieldnames:
            raise ValueError(f"CSVの列名が想定と違います: {reader.fieldnames}")

        for i, row in enumerate(reader, start=2):  # header is line 1
            name = (row.get("名前") or "").strip()
            score_s = (row.get("スコア") or "").strip()
            if not name:
                raise ValueError(f"{i}行目: 名前が空です")
            try:
                score = int(score_s)
            except Exception as e:
                raise ValueError(f"{i}行目: スコアが整数ではありません: {score_s!r}") from e

            scores_by_person.setdefault(name, []).append(score)

    return scores_by_person


def print_summary(scores_by_person: dict[str, list[int]]) -> None:
    rows: list[tuple[str, Stats]] = []
    for name, scores in scores_by_person.items():
        rows.append((name, calc_stats(scores)))

    rows.sort(key=lambda x: x[0])

    name_w = max(len("名前"), *(len(n) for n, _ in rows)) if rows else len("名前")
    header = f"{'名前':<{name_w}}  {'件数':>4}  {'平均':>7}  {'最高':>4}  {'最低':>4}"
    print(header)
    print("-" * len(header))

    for name, st in rows:
        print(f"{name:<{name_w}}  {st.count:>4}  {st.avg:>7.2f}  {st.max_:>4}  {st.min_:>4}")


def main() -> None:
    # Windows端末で日本語が文字化けしやすいので、可能ならUTF-8に揃える
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

    csv_path = Path(__file__).with_name("課題2.csv")
    scores_by_person = read_scores_by_person(csv_path)
    print_summary(scores_by_person)


if __name__ == "__main__":
    main()
