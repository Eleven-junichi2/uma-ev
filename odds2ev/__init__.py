import pandas as pd


def prediction(
    racecard: pd.DataFrame,
    factors_list: tuple[pd.DataFrame],
    weights: dict,
    pipelines: dict,
):
    result_df = racecard.copy()
    
    for factors in factors_list:
        merge_key = factors.columns.values[0]
        result_df.merge(factors, how="left", on=merge_key)
    print(result_df)


# def prediction(
#     df_racecard: pd.DataFrame,
#     df_ev_score_factors: pd.DataFrame,
#     df_ev_prob_factors: pd.DataFrame,
#     ev_factors_weights: dict[str, float],
# ) -> pd.DataFrame:
#     """
#     Args:
#         df_racecard: 出馬表
#         df_ev_score_factors: スコア系要因 (Softmax)
#         df_ev_prob_factors: 確率系要因 (Normalize)
#         ev_factors_weights: 重み
#     """
#     # 1. データの結合
#     df_result = df_racecard.copy()

#     # スコア要因の結合（存在すれば）
#     if df_ev_score_factors is not None and len(df_ev_score_factors.columns) > 1:
#         df_result = pd.merge(df_result, df_ev_score_factors, on="馬名", how="left")

#     # 確率要因の結合（存在すれば）
#     if df_ev_prob_factors is not None and len(df_ev_prob_factors.columns) > 1:
#         df_result = pd.merge(df_result, df_ev_prob_factors, on="馬名", how="left")

#     # 2. オッズ順ソート
#     df_result = df_result.sort_values(by="オッズ", ascending=True).reset_index(
#         drop=True
#     )

#     win_rate = np.zeros(len(df_result))

#     # 3. 計算ループ
#     for factor, weight in ev_factors_weights.items():
#         # 重みが0の場合は計算スキップ
#         if weight <= 0:
#             continue

#         vals_normalized = None

#         # --- パターンA: 統計データ ---
#         if factor == WIN_RATE_BY_FAVORITE_LABELNAME:
#             vals_normalized = df_result.index.map(
#                 lambda x: WIN_RATE_BY_FAVORITE[x]
#                 if x < len(WIN_RATE_BY_FAVORITE)
#                 else 0.0
#             ).to_numpy()

#         # --- パターンB: その他の要因 ---
#         else:
#             # データ存在チェック
#             if factor not in df_result.columns:
#                 raise ValueError(
#                     f"指定された要因 '{factor}' が結合後のデータに存在しません。"
#                 )

#             vals = df_result[factor].fillna(0).to_numpy()

#             # ケース1: 確率系 (prob_factors由来) -> 単純正規化
#             if df_ev_prob_factors is not None and factor in df_ev_prob_factors.columns:
#                 total = np.sum(vals)
#                 if total > 0:
#                     vals_normalized = vals / total
#                 else:
#                     vals_normalized = np.zeros_like(vals)

#             # ケース2: スコア系 (score_factors由来) -> Softmax
#             elif (
#                 df_ev_score_factors is not None
#                 and factor in df_ev_score_factors.columns
#             ):
#                 if vals.std() == 0:
#                     vals_normalized = np.full(len(vals), 1.0 / len(vals))
#                 else:
#                     z_score = (vals - vals.mean()) / vals.std()
#                     vals_normalized = softmax(z_score)

#             else:
#                 vals_normalized = np.zeros_like(vals)

#         # 寄与分を計算して列として保存
#         contribution = vals_normalized * weight
#         col_name = f"寄与_{factor}"
#         df_result[col_name] = contribution

#         win_rate += contribution

#     # 結果計算
#     df_result["統合勝率"] = win_rate
#     df_result["対数期待値"] = np.log(df_result["オッズ"] * df_result["統合勝率"])
#     df_result["対数補正オッズ期待値"] = np.log(df_result["オッズ"]) * df_result["統合勝率"]

#     return df_result.sort_values(by="対数補正オッズ期待値", ascending=False).reset_index(
#         drop=True
#     )
