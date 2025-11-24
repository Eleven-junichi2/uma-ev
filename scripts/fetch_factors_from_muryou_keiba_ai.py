from pathlib import Path
import argparse

import pandas as pd

from __init__ import parser_finder
from umaev.scraping import fetch_html


def run(url: str | None = None, output_filepath: Path | None = None) -> pd.DataFrame:
    if url is None:
        url = input("予想表示ページのurlを入力してください：")

    if parser := parser_finder.find(url):
        df = parser(fetch_html(url))

    print(df)

    if output_filepath:
        df.to_csv(output_filepath, index=False, encoding="utf-8-sig")
        print(f"次の場所に保存しました: {output_filepath}")
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Netkeibaの出馬表を取得します")
    parser.add_argument(
        "-u", "--url", type=str, help="予想表示ページのurl"
    )
    parser.add_argument(
        "-o",
        "--output-filepath",
        type=Path,
        help="保存先のファイルパス (指定しない場合は保存しません)",
    )
    args = parser.parse_args()
    run(url=args.url, output_filepath=args.output_filepath)
