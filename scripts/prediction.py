from pathlib import Path
import argparse
import json

import pandas as pd

import __init__  # noqa: F401
from umaev.predictor import prediction
from umaev.calc import normalize, softmax, standardize, identity


def run(recipe_filepath: Path, data_dir: Path, output_dir: Path):
    with open(recipe_filepath, encoding="utf-8") as f:
        recipe = json.load(f)
    # recipe["racecard"]の名前のcsvを探しracecardを設定
    race_dir = data_dir / "race" / recipe['race_date'] / recipe["racecourse"] / recipe["race_num"]
    racecard = pd.read_csv(race_dir / "racecard.csv")
    # ---
    factors_list: list[pd.DataFrame] = []
    for factor in recipe["factors"]:
        factor_filepath = data_dir / "factors" / rf"{factor}.csv"
        if factor_filepath.exists():
            print(f"Loaded global factor: {factor}") # デバッグ用
            factors_list.append(pd.read_csv(factor_filepath))
        race_factor_filepath = race_dir / "factors" / rf"{factor}.csv"
        if race_factor_filepath.exists():
            print(f"Loaded race factor: {factor}") # デバッグ用
            factors_list.append(pd.read_csv(race_factor_filepath))
    df = prediction(
        racecard=racecard,
        factors_list=factors_list,
        pipelines=recipe["pipelines"],
        operations={
            "normalize": normalize,
            "softmax": softmax,
            "standardize": standardize,
            "identity": identity,
        },
        weights=recipe["weights"],
    )
    print(df)
    output_dir.mkdir(exist_ok=True)
    save_filepath = output_dir / rf"{recipe['race_date']}_{recipe["racecourse"]}_{recipe["race_num"]}"
    df.to_csv(save_filepath.with_suffix(".csv"))
    df.to_html(save_filepath.with_suffix(".html"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="レシピに基づいて競馬予想（期待値計算）を実行します"
    )
    parser.add_argument(
        "recipe_path", type=Path, help="レシピJSONファイルのパス (例: recipe.json)"
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data"),
        help="使用データのルートディレクトリ (default: data)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output"),
        help="結果の出力ファイルのディレクトリ (default: output)",
    )

    args = parser.parse_args()

    run(
        recipe_filepath=args.recipe_path,
        data_dir=args.data_dir,
        output_dir=args.output_dir,
    )
