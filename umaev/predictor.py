from collections.abc import Callable
import numpy as np
import pandas as pd


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
    df["勝率"] = 0.0
    total_weight = 0.0
    for factor_label, w in weights.items():
        df["勝率"] += calc_df[factor_label] * w
        total_weight += w
    if total_weight > 1.0:
        df["勝率"] /= total_weight
    df["期待値"] = df["オッズ"] * df["勝率"]
    df["対数期待値"] = np.log(df["期待値"])
    df["対数オッズ期待値"] = np.log(df["オッズ"]) * df["勝率"]
    df = df.sort_values("勝率", ascending=False)
    return df
