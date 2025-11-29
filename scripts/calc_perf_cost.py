from pathlib import Path

import pandas as pd


def race_perf_cost(
    P_c: float, S_c: float, S_s: float, P_s: float, D: float, D_f: float, K_t: float, L_h: float, W: int, K_s: float = 0
) -> float:
    V_c = S_c * P_c
    V_s = S_s * P_s
    K_w = 1 - (500 / W) ** 2
    K_h = L_h * 0.1
    K_f = K_t + K_s - K_h - K_w
    if K_f > 1.0:
        K_f = 1.0
    R_csp = S_c / P_c
    R_ssp = S_s / P_s
    K_ca = R_csp * (1.0 - K_f)
    K_sa = R_ssp * (1.0 - K_f)
    D_m = D - D_f
    V_tc = V_c * K_f
    V_ts = V_s * K_f
    return (D_m * (1 + K_ca) / V_tc) + (D_f * (1 + K_sa) / V_ts)


def estimate_race_time(
    P_c: float, S_c: float, S_s: float, P_s: float, D: float, K_t: float, L_h: float, W: int, K_s: float = 0
) -> float:
    V_c = S_c * P_c
    V_s = S_s * P_s
    K_w = 1 - (500 / W) ** 2
    K_h = L_h * 0.1
    K_f = K_t + K_s - K_h - K_w
    if K_f > 1.0:
        K_f = 1.0
    V_tc = V_c * K_f
    V_ts = V_s * K_f
    return ((D*7/10)/V_tc)+((D*3/10)/V_ts)

perf_cost_data = {"馬名": [], "レース発揮コスト": [], "巡航スピード": []}
horse_running_data = pd.read_csv(Path("data/factors/2025-11-29_京都_11.csv"))
perf_cost_df = pd.DataFrame(horse_running_data)
perf_cost_df["巡航スピード"] = (
    perf_cost_df["巡航ピッチ"] * perf_cost_df["巡航ストライド"]
)
perf_cost_df["スパートスピード"] = (
    perf_cost_df["スパートピッチ"] * perf_cost_df["スパートストライド"]
)
perf_cost_df["レース発揮コスト"] = perf_cost_df.apply(
    lambda row: race_perf_cost(
        P_c=row["巡航ピッチ"],
        S_c=row["巡航ストライド"],
        P_s=row["スパートピッチ"],
        S_s=row["スパートストライド"],
        D=2000,
        D_f=323.4,
        K_t=1,
        L_h=row["後肢踏み込み"],
        W=500,
    ),
    axis=1,
)
perf_cost_df["推定走破タイム"] = perf_cost_df.apply(
    lambda row: estimate_race_time(
        P_c=row["巡航ピッチ"],
        S_c=row["巡航ストライド"],
        P_s=row["スパートピッチ"],
        S_s=row["スパートストライド"],
        D=2000,
        K_t=0.9,
        L_h=row["後肢踏み込み"],
        W=500,
    ),
    axis=1,
)
for sort_key, ascending in (("レース発揮コスト", True), ("推定走破タイム", True), ("巡航スピード", False), ("スパートスピード", False)):
    print(f"<<{sort_key} {'昇' if ascending else '降'}順>>")
    print(perf_cost_df[["馬名", sort_key]].sort_values(sort_key, ascending=ascending))

# print("フリーガー:", race_perf_cost(P_c=2.570694087, S_c=5.593464052, D=2000, K_t=1.0, K_s=0.7, K_h=0.3, W=446))
# print("バルセシート:", race_perf_cost(P_c=2.570694087, S_c=5.593464052, D=2000, K_t=1.0, K_s=0.7, K_h=0.3, W=446))
