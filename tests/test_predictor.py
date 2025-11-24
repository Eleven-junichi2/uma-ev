import pandas as pd

from umaev.transforms import normalize, softmax
from umaev.predictor import prediction

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