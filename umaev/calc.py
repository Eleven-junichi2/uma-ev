import numpy as np
import pandas as pd


def normalize(s: pd.Series) -> pd.Series:
    return s / s.sum() if s.sum() != 0 else s


def softmax(s: pd.Series) -> pd.Series:
    # オーバーフロー対策
    exp_x = np.exp(s - np.max(s))
    return exp_x / exp_x.sum()


def standardize(s: pd.Series) -> pd.Series:
    """標準化 (Z-score normalization)"""
    if s.std() == 0:
        return s - s.mean()  # 分散0の場合は全て0にする
    return (s - s.mean()) / s.std()


def identity(x: pd.Series) -> pd.Series:
    return x


def race_perf_cost(
    race_distance: int,
    pitch_cruise: float,
    stride_cruise: float,
    track_condition_coef: float,
    stability_coef: float,
    hind_leg_sink_coef: float,
    weight_coef: float,
    prev_race_opening_pace_avg: float,
) -> float:
    speed_cruise = stride_cruise * pitch_cruise
    running_form_load_coef = (
        track_condition_coef + stability_coef - hind_leg_sink_coef - weight_coef
    )
    return (
        race_distance
        * (1 + (stride_cruise / pitch_cruise) * (1.0 - running_form_load_coef))
    ) / (speed_cruise * running_form_load_coef * prev_race_opening_pace_avg)
