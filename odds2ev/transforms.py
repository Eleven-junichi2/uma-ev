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
        return s - s.mean() # 分散0の場合は全て0にする
    return (s - s.mean()) / s.std()
