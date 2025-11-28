from pathlib import Path
import json
import argparse

import pandas as pd

import __init__  # noqa

from umaev.scraping import fetch_html
import html_parsers.netkeiba


def run(
    race_id: str | None = None,
    date_to_race_id_filepath: Path | None = None,
    race_date: str | None = None,
    race_course: str | None = None,
    race_num: str | None = None,
    output_dir: Path | None = None,
) -> pd.DataFrame:
    if date_to_race_id_filepath:
        if date_to_race_id_filepath.exists():
            with open(date_to_race_id_filepath, "r", encoding="utf-8") as f:
                date_to_race_id = json.load(f)
                if race_date is None and race_course is None and race_num is None:
                    print(
                        "レース情報取得のために、開催日・レース番号からnetkeibaレースidを検索します。"
                    )
                if race_date is None:
                    race_date = input("開催日程（書式：西暦4桁-月2桁-日2桁）を入力：")
                if race_course is None:
                    race_course = input("競馬場を入力：")
                if race_num is None:
                    race_num = input("レース番号を入力：")
                race_id = date_to_race_id[race_date][race_course][race_num]
    if race_id is None:
        race_id = input("netkeibaレースidを入力：")

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
    parser = argparse.ArgumentParser(
        description="netkeibaからレース情報（出馬表等）を取得します"
    )
    parser.add_argument(
        "-r", "--race-id", type=str, help="取得するレースを指定するためのnetkeibaレースID。指定しない場合、日程・レース番号キーで指定する方法を利用してください"
    )
    parser.add_argument(
        "-m",
        "--date-to-race-id-filepath",
        type=Path,
        help="開催日程・レース番号とnetkeibaのレースidの対応を記録したjsonファイルのパス",
    )
    parser.add_argument(
        "-d",
        "--race-date",
        type=str,
        help="レース開催日程。netkeibaレースid辞書からidを検索するために利用される",
    )
    parser.add_argument(
        "-c",
        "--race-course",
        type=str,
        help="レースが開催される競馬場。netkeibaレースid辞書からidを検索するために利用される",
    )
    parser.add_argument(
        "-n",
        "--race-num",
        type=str,
        help="レース番号。netkeibaレースid辞書からidを検索するために利用される",
    )    
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        help="保存先のディレクトリパス (指定しない場合は保存しません)",
    )
    args = parser.parse_args()
    run(
        race_id=args.race_id,
        date_to_race_id_filepath=args.date_to_race_id_filepath,
        race_course=args.race_course,
        race_date=args.race_date,
        race_num=args.race_num,
        output_dir=args.output_dir,
    )
