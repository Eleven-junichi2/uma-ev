import json
from pathlib import Path
import argparse

import __init__  # noqa

from umaev.scraping import fetch_html
import html_parsers.netkeiba


def run(
    date: str | None = None,
    output_filepath: Path | None = None,
) -> dict:
    if date is None:
        date = input("開催日程を入力してください：")
    url = rf"https://race.netkeiba.com/top/race_list.html?kaisai_date={date}"
    html = fetch_html(url)
    new_date2race_id_data = html_parsers.netkeiba.race_date_to_race_id(html)
    date2race_id = {}
    if output_filepath:
        if output_filepath.exists():
            with open(output_filepath, "r", encoding="utf-8") as f:
                date2race_id = json.load(f)
    date2race_id.update(new_date2race_id_data)
    if output_filepath:
        with open(output_filepath, "w", encoding="utf-8") as f:
            json.dump(date2race_id, f, ensure_ascii=False, indent=4)
            print(f"保存しました：{output_filepath}")
    print(date2race_id)
    return date2race_id


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Netkeibaからレース情報（出馬表等）を取得します"
    )
    parser.add_argument(
        "-d",
        "--date",
        type=str,
        help="開催日程（書式：西暦4桁月2桁日2桁、例：20250112）",
    )
    parser.add_argument("-r", "--race-num", type=int, help="レース番号")
    parser.add_argument(
        "-o", "--output-filepath", type=Path, help="更新（保存）先jsonファイルのパス(指定しないと保存しません)"
    )
    args = parser.parse_args()
    run(date=args.date, output_filepath=args.output_filepath)
