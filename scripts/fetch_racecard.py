from pathlib import Path
import argparse

import pandas as pd

from __init__ import parser_finder
from odds2ev.scraping import fetch_html


def run(race_id: str | None = None, output_dir: Path | None = None) -> pd.DataFrame:
    if race_id is None:
        race_id = input("netkeibaレースidを入力してください：")

    url = rf"https://race.netkeiba.com/odds/index.html?race_id={race_id}"
    if parser := parser_finder.find(url):
        racecard = parser(fetch_html(url))

    print(racecard)

    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        save_path = output_dir / f"{race_id}.csv"
        racecard.to_csv(save_path, index=False, encoding="utf-8-sig")
        print(f"次の場所に保存しました: {save_path}")
    return racecard


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Netkeibaの出馬表を取得します")
    parser.add_argument(
        "-i", "--race-id", type=str, help="NetkeibaのレースID (例: 202501010101)"
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        help="保存先のディレクトリパス (指定しない場合は保存しません)",
    )
    args = parser.parse_args()
    run(race_id=args.race_id, output_dir=args.output_dir)
