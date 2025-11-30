from pathlib import Path
import json
import argparse
import random
import sys
import time

import pandas as pd
import requests

import __init__  # noqa

from umaev.scraping import fetch_html
from html_parsers import netkeiba


def run(
    name2netkeiba_horse_id_filepath: Path,
    output_filepath: Path | None = None,
):
    # TODO:すでに取得している馬の血統のデータ取得を避ける
    if not name2netkeiba_horse_id_filepath.exists():
        print(
            f"エラー：辞書ファイル{name2netkeiba_horse_id_filepath}が見つかりませんでした"
        )
        sys.exit(1)
    with open(name2netkeiba_horse_id_filepath, "r", encoding="utf-8") as f:
        name2horse_id: dict[str, str] = json.load(f)
    pedigrees = []
    for name, id in name2horse_id.items():
        url = rf"https://db.netkeiba.com/horse/ped/{id}/"
        # print(url)
        # response = requests.get(url)
        # print(response.status_code)
        pedigree = netkeiba.pedigree(fetch_html(url))
        pedigrees.append(pedigree)
        wait_time = random.randint(20, 40)  # sec = randint / 10
        for tick in range(0, wait_time):
            print(
                f"\r\033[K{name}を処理中: {tick / 10}/{wait_time / 10}",
                end="",
                flush=True,
            )
            time.sleep(0.1)
        print(f"\r\033[K{name}: 完了", flush=True)
    new_pedigree_df = pd.DataFrame(pedigrees)
    print(new_pedigree_df)
    if output_filepath:
        # todo: 既存ファイルの更新
        pedigree_df = pd.DataFrame()
        if output_filepath.exists():
            pedigree_df = pd.read_csv(output_filepath)
        pedigree_df = pd.concat([pedigree_df, new_pedigree_df], ignore_index=True)
        pedigree_df = pedigree_df.drop_duplicates(subset=["馬名"], keep="last")
        pedigree_df.to_csv(output_filepath, index=False)
        print(f"保存しました：{output_filepath}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="netkeibaからレース情報（出馬表等）を取得します"
    )
    parser.add_argument(
        "-m",
        "--name2netkeiba-horse-id-filepath",
        type=Path,
        help="馬名に対応するnetkeiba馬idの辞書の保存先ファイルパス(指定しない場合は保存しません)",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--output-filepath",
        type=Path,
        help="保存先",
    )
    args = parser.parse_args()
    run(
        name2netkeiba_horse_id_filepath=args.name2netkeiba_horse_id_filepath,
        output_filepath=args.output_filepath,
    )
