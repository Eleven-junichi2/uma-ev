from pathlib import Path
import json
import argparse
import sys

import __init__  # noqa

from umaev.scraping import fetch_html
import html_parsers.netkeiba


def run(
    race_date: str,
    race_course: str,
    race_num: str,
    date2netkeiba_race_id_filepath: Path,
    name2netkeiba_horse_id_filepath: Path | None = None,
):
    """レース日程・競馬場・レース番号から特定されるレースの出馬表・情報をnetkeibaから取得します。
    取得データのファイルへの保存、出走馬とhorse_idの対応のマップファイルへの保存も行います。
    """
    if date2netkeiba_race_id_filepath.exists():
        with open(date2netkeiba_race_id_filepath, "r", encoding="utf-8") as f:
            date_to_race_id = json.load(f)
            race_id = date_to_race_id[race_date][race_course][race_num]
    else:
        print(
            "エラー：レース日程とnetkeibaレースidの対応記載マップファイルが見つかりません"
        )
        sys.exit(1)

    url = rf"https://race.netkeiba.com/race/shutuba.html?race_id={race_id}"
    html = fetch_html(url)
    racecard = html_parsers.netkeiba.racecard(html)
    raceinfo = html_parsers.netkeiba.raceinfo(html)

    print(racecard)
    print(raceinfo)

    new_name2netkeiba_horse_id_data = (
        html_parsers.netkeiba.name_to_horse_id_from_racecard(html)
    )

    race_dir = Path(f"data/race/{race_date}/{race_course}/{race_num}/")
    race_dir.mkdir(parents=True, exist_ok=True)
    racecard.to_csv(race_dir / "racecard.csv", index=False, encoding="utf-8-sig")
    with open(race_dir / "raceinfo.json", "w", encoding="utf-8") as f:
        json.dump(raceinfo, f, ensure_ascii=False, indent=4)
    print(f"次のディレクトリに保存しました: {race_dir}")

    # 出走馬とhorse_idの対応のマップファイルを更新する処理：
    if name2netkeiba_horse_id_filepath:
        name2netkeiba_horse_id = {}
        if name2netkeiba_horse_id_filepath.exists():
            with open(name2netkeiba_horse_id_filepath, "r", encoding="utf-8") as f:
                name2netkeiba_horse_id = json.load(f)
        name2netkeiba_horse_id.update(new_name2netkeiba_horse_id_data)
        with open(name2netkeiba_horse_id_filepath, "w", encoding="utf-8") as f:
            json.dump(name2netkeiba_horse_id, f, ensure_ascii=False, indent=4)
        print(f"次のパスに保存しました: {name2netkeiba_horse_id_filepath}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=run.__doc__.splitlines()[0]  # pyright: ignore[reportOptionalMemberAccess]
    )
    parser.add_argument(
        "-d",
        "--race-date",
        type=str,
        help="レース開催日程。netkeibaレースid辞書からidを検索するために利用される",
        required=True,
    )
    parser.add_argument(
        "-c",
        "--race-course",
        type=str,
        help="レースが開催される競馬場。netkeibaレースid辞書からidを検索するために利用される",
        required=True,
    )
    parser.add_argument(
        "-n",
        "--race-num",
        type=str,
        help="レース番号。netkeibaレースid辞書からidを検索するために利用される",
        required=True,
    )
    parser.add_argument(
        "-r",
        "-d2r",
        "--date2netkeiba-race-id-filepath",
        type=Path,
        help="馬名に対応するnetkeiba馬idの辞書の保存先ファイルパス(指定しない場合は保存しません)",
        required=True,
    )
    parser.add_argument(
        "-u",
        "-n2h",
        "--name2netkeiba-horse-id-filepath",
        type=Path,
        help="馬名に対応するnetkeiba馬idの辞書の保存先ファイルパス(指定しない場合は保存しません)",
    )
    args = parser.parse_args()
    run(
        race_course=args.race_course,
        race_date=args.race_date,
        race_num=args.race_num,
        date2netkeiba_race_id_filepath=args.date2netkeiba_race_id_filepath,
        name2netkeiba_horse_id_filepath=args.name2netkeiba_horse_id_filepath,
    )
