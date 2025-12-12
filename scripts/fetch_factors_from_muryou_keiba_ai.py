from pathlib import Path
import argparse

import pandas as pd

import __init__  # noqa

from umaev.scraping import fetch_html
from html_parsers import muryou_keiba_ai


def run(url: str | None = None, output_filepath: Path | None = None) -> pd.DataFrame:
    if url is None:
        url = input("予想表示ページのurlを入力してください：")
    html = fetch_html(url)
    df = muryou_keiba_ai.ai_prediction_card(html)
    race_date, race_course, race_num = muryou_keiba_ai.race_date_course_num(html)
    print(df)
    if output_filepath:
        df.to_csv(output_filepath, index=False, encoding="utf-8-sig")
        print(f"次の場所に保存しました: {output_filepath}")
    else:
        output_filepath = Path(
            f"data/race/{race_date}/{race_course}/{race_num}/factors/無料競馬AI.csv"
        )
        output_filepath.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_filepath, index=False)
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="無料競馬AIの予想を取得します")
    parser.add_argument("-u", "--url", type=str, help="予想表示ページのurl")
    parser.add_argument(
        "-o",
        "--output-filepath",
        type=Path,
        help="保存先のファイルパス（指定なしの場合デフォルトの場所に保存）",
    )
    args = parser.parse_args()
    run(url=args.url, output_filepath=args.output_filepath)
