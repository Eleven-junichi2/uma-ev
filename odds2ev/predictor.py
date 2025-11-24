from collections.abc import Callable
import numpy as np
import pandas as pd

from utils import softmax, normalize


def prediction(
    racecard: pd.DataFrame,
    factors_list: list[pd.DataFrame],
    weights: dict[str, float],
    operations: dict[str, Callable[..., pd.Series]],
    pipelines: dict[str, list[str]],
) -> pd.DataFrame:
    df = racecard.copy()
    for factors in factors_list:
        join_key = factors.columns[0]
        df = df.merge(factors, how="left", on=join_key)
    # パイプラインの処理
    calc_df = pd.DataFrame()
    calc_df.index = df.index
    for factor_label, ops_list in pipelines.items():
        series = df[factor_label]
        for ops in ops_list:
            series = operations[ops](series)
        calc_df[factor_label] = series
    # ---
    print(calc_df)
    df["勝率"] = 0.0
    total_weight = 0.0
    for factor_label, w in weights.items():
        df["勝率"] += calc_df[factor_label] * w
        total_weight += w
    if total_weight > 1.0:
        df["勝率"] /= total_weight
    return df


def test():
    racecard = pd.DataFrame(
        {
            "馬名": ["ホープ", "ファミリー", "ハピネス"],
            "オッズ": [2.5, 1.8, 5.0],
            "人気": [2, 1, 3],
        }
    )
    print("racecard:", racecard)

    factors_list = [
        pd.DataFrame({"人気": [1, 2, 3], "人気別勝率": [0.327, 0.192, 0.132]}),
        pd.DataFrame(
            {"馬名": ["ファミリー", "ハピネス", "ホープ"], "血統評価": [3, 1, 2]}
        ),
    ]
    print("factors_list:", factors_list)
    print()
    operations = {
        "normalize": normalize,
        "softmax": softmax,
    }
    recipe = {
        "racecard": "example",
        "factors": ["win_rate_by_popularity", "example"],
        "pipelines": {"人気別勝率": ["normalize"], "血統評価": ["softmax"]},
        "weights": {"人気別勝率": 7, "血統評価": 3},
    }
    df = prediction(
        racecard=racecard,
        factors_list=factors_list,
        pipelines=recipe["pipelines"],
        operations=operations,
        weights=recipe["weights"],
    )
    print(df)
    testcase = pd.DataFrame(
        {
            "馬名": ["ホープ", "ファミリー", "ハピネス"],
            "オッズ": [2.5, 1.8, 5.0],
            "人気": [2, 1, 3],
            "人気別勝率": [0.192, 0.327, 0.132],
            "血統評価": [2, 3, 1],
            "勝率": [0.279870, 0.551185, 0.168945],
        }
    )
    pd.testing.assert_frame_equal(df, testcase)
    recipe["weights"] = {"人気別勝率": 0.7, "血統評価": 0.3}
    df = prediction(
        racecard=racecard,
        factors_list=factors_list,
        pipelines=recipe["pipelines"],
        operations=operations,
        weights=recipe["weights"],
    )
    print(df)
    pd.testing.assert_frame_equal(df, testcase)


if __name__ == "__main__":
    test()
