import numpy as np
import pandas as pd


def normalize(s: pd.Series) -> pd.Series:
    return s / s.sum() if s.sum() != 0 else s


def softmax(s: pd.Series) -> pd.Series:
    # オーバーフロー対策
    exp_x = np.exp(s - np.max(s))
    return exp_x / exp_x.sum()
