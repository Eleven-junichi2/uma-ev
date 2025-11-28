import json
from pathlib import Path
import argparse

import pandas as pd

import __init__ # noqa

from umaev.scraping import fetch_html
import html_parsers.netkeiba

def run(race_id: str | None = None, output_dir: Path | None = None) -> pd.DataFrame:
    if race_id is None:
        race_id = input("netkeibaレースidを入力してください：")

    url = rf"https://race.netkeiba.com/race/shutuba.html?race_id={race_id}"
    html = fetch_html(url)
    racecard = html_parsers.netkeiba.racecard(html)
    raceinfo = html_parsers.netkeiba.raceinfo(html)

    print(racecard)
    print(raceinfo)

    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        racecard.to_csv(output_dir / "racecard.csv", index=False, encoding="utf-8-sig")
        with open(output_dir / "raceinfo.json", "w", encoding="utf-8") as f:
            json.dump(raceinfo, f, ensure_ascii=False, indent=4)
        print(f"次のディレクトリに保存しました: {output_dir}")
    return racecard


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Netkeibaからレース情報（出馬表等）を取得します")
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
