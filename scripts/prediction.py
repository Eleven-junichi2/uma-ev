from pathlib import Path
import argparse
import json

import pandas as pd

import __init__  # noqa: F401
from umaev.predictor import prediction
from umaev.transforms import normalize, softmax, standardize


def run(recipe_filepath: Path, data_dir: Path, output_dir: Path):
    with open(recipe_filepath, encoding="utf-8") as f:
        recipe = json.load(f)
    # recipe["racecard"]の名前のcsvを探しracecardを設定
    racecard = pd.read_csv(data_dir / "racecards" / rf"{recipe['racecard']}.csv")
    # ---
    factors_list: list[pd.DataFrame] = []
    for factors in recipe["factors"]:
        factors_list.append(pd.read_csv(data_dir / "factors" / rf"{factors}.csv"))
    df = prediction(
        racecard=racecard,
        factors_list=factors_list,
        pipelines=recipe["pipelines"],
        operations={
            "normalize": normalize,
            "softmax": softmax,
            "standardize": standardize,
        },
        weights=recipe["weights"],
    )
    print(df)
    output_dir.mkdir(exist_ok=True)
    df.to_csv(output_dir / rf"{recipe['racecard']}.csv")


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
