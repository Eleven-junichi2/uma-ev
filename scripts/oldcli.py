# TODO: コードの整理
# TODO: ev_factorsで扱える結合キーとして「人気」を追加する

import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup


from odds2ev.scraping import extract_racecard_from_netkeiba_html

WIN_RATE_BY_FAVORITE = (
    0.327,
    0.192,
    0.132,
    0.095,
    0.072,
    0.054,
    0.039,
    0.027,
    0.021,
    0.017,
    0.013,
    0.01,
    0.007,
    0.004,
    0.004,
    0.002,
    0.001,
    0.001,
)
WIN_RATE_BY_FAVORITE_LABELNAME = "人気別勝率"





def extract_racecard_from_netkeiba_html(html_data: str) -> pd.DataFrame:
    soup = BeautifulSoup(html_data, "html.parser")
    html_table = soup.find("table", {"class": "RaceOdds_HorseList_Table"})
    dataframe = pd.DataFrame()
    if html_table is None:
        print("データ取得先のテーブルが見つかりませんでした。")
        print("URLやレースIDが正しいか確認してください。")
        sys.exit(1)
    for html_row in html_table.find_all("tr", {"id": re.compile(r"ninki-data-\d+")}):
        htmlclass2field = {"Horse_Name": "馬名", "Odds": "オッズ"}
        row_data = {}
        for class_ in htmlclass2field.keys():
            if data := html_row.find("td", {"class": class_}):
                if class_ == "Odds":
                    if data := data.find("span", {"id": re.compile(r"odds-1_\d+")}):
                        row_data[htmlclass2field[class_]] = data.get_text()
                    else:
                        row_data[htmlclass2field[class_]] = None
                else:
                    row_data[htmlclass2field[class_]] = data.get_text()
        dataframe = pd.concat([dataframe, pd.DataFrame([row_data])], ignore_index=True)
    dataframe["オッズ"] = pd.to_numeric(dataframe["オッズ"], errors="coerce")
    return dataframe


def netkeiba_race_id_prompt(default_race_id="202505050611") -> str:
    race_id = input(f"レースIDを入力してください (デフォルト: {default_race_id}): ")
    if race_id == "":
        race_id = default_race_id
    return race_id


def input_ev_factors_manually(
    df_racecard: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    手動入力を行い、スコア系(df_scores)と確率系(df_probs)の2つのDataFrameを返す
    """
    print("\n--- 期待値計算要因の新規作成 ---")

    # ベースのDataFrame作成
    df_scores = df_racecard[["馬名"]].copy()
    df_probs = df_racecard[["馬名"]].copy()

    while True:
        print("\n新しい評価軸（列）を追加しますか？")
        print("入力例: 'タイム指数', 'AI勝率' (Enterのみで完了)")
        col_name = input("列名: ").strip()

        if not col_name:
            break

        # 重複チェック
        if col_name in df_scores.columns or col_name in df_probs.columns:
            print("その列名は既に存在します。")
            continue

        # タイプの選択
        print(f"'{col_name}' のデータタイプを選んでください:")
        print("1: スコア・指数 (偏差値評価 -> Softmax)")
        print("2: 確率・勝率 (単純割合 -> Normalize)")
        type_choice = input("選択 (1/2): ").strip()

        target_df = None
        if type_choice == "1":
            target_df = df_scores
        elif type_choice == "2":
            target_df = df_probs
        else:
            print("無効な選択です。最初からやり直してください。")
            continue

        print(f"--- '{col_name}' の値を各馬に入力してください ---")
        values = []
        for horse in df_racecard["馬名"]:
            while True:
                val_str = input(f"{horse}: ")
                if val_str == "":
                    val = 0.0
                    break
                try:
                    val = float(val_str)
                    values.append(val)
                    break
                except ValueError:
                    print("数値を入力してください。")

        target_df[col_name] = values

    return df_scores, df_probs


def softmax(x: np.ndarray):
    """ソフトマックス関数: 数値の配列を確率分布（合計1.0）に変換する"""
    if np.all(x == x[0]):
        return np.full(x.shape, 1.0 / len(x))
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()


def prediction(
    df_racecard: pd.DataFrame,
    df_ev_score_factors: pd.DataFrame,
    df_ev_prob_factors: pd.DataFrame,
    ev_factors_weights: dict[str, float],
) -> pd.DataFrame:
    """
    Args:
        df_racecard: 出馬表
        df_ev_score_factors: スコア系要因 (Softmax)
        df_ev_prob_factors: 確率系要因 (Normalize)
        ev_factors_weights: 重み
    """
    # 1. データの結合
    df_result = df_racecard.copy()

    # スコア要因の結合（存在すれば）
    if df_ev_score_factors is not None and len(df_ev_score_factors.columns) > 1:
        df_result = pd.merge(df_result, df_ev_score_factors, on="馬名", how="left")

    # 確率要因の結合（存在すれば）
    if df_ev_prob_factors is not None and len(df_ev_prob_factors.columns) > 1:
        df_result = pd.merge(df_result, df_ev_prob_factors, on="馬名", how="left")

    # 2. オッズ順ソート
    df_result = df_result.sort_values(by="オッズ", ascending=True).reset_index(
        drop=True
    )

    win_rate = np.zeros(len(df_result))

    # 3. 計算ループ
    for factor, weight in ev_factors_weights.items():
        # 重みが0の場合は計算スキップ
        if weight <= 0:
            continue

        vals_normalized = None

        # --- パターンA: 統計データ ---
        if factor == WIN_RATE_BY_FAVORITE_LABELNAME:
            vals_normalized = df_result.index.map(
                lambda x: WIN_RATE_BY_FAVORITE[x]
                if x < len(WIN_RATE_BY_FAVORITE)
                else 0.0
            ).to_numpy()

        # --- パターンB: その他の要因 ---
        else:
            # データ存在チェック
            if factor not in df_result.columns:
                raise ValueError(
                    f"指定された要因 '{factor}' が結合後のデータに存在しません。"
                )

            vals = df_result[factor].fillna(0).to_numpy()

            # ケース1: 確率系 (prob_factors由来) -> 単純正規化
            if df_ev_prob_factors is not None and factor in df_ev_prob_factors.columns:
                total = np.sum(vals)
                if total > 0:
                    vals_normalized = vals / total
                else:
                    vals_normalized = np.zeros_like(vals)

            # ケース2: スコア系 (score_factors由来) -> Softmax
            elif (
                df_ev_score_factors is not None
                and factor in df_ev_score_factors.columns
            ):
                if vals.std() == 0:
                    vals_normalized = np.full(len(vals), 1.0 / len(vals))
                else:
                    z_score = (vals - vals.mean()) / vals.std()
                    vals_normalized = softmax(z_score)

            else:
                vals_normalized = np.zeros_like(vals)

        # 寄与分を計算して列として保存
        contribution = vals_normalized * weight
        col_name = f"寄与_{factor}"
        df_result[col_name] = contribution

        win_rate += contribution

    # 結果計算
    df_result["統合勝率"] = win_rate
    df_result["対数期待値"] = np.log(df_result["オッズ"] * df_result["統合勝率"])
    df_result["対数補正オッズ期待値"] = np.log(df_result["オッズ"]) * df_result["統合勝率"]

    return df_result.sort_values(by="対数補正オッズ期待値", ascending=False).reset_index(
        drop=True
    )


def main():
    if len(sys.argv) > 1:
        race_id = sys.argv[1]
    else:
        race_id = netkeiba_race_id_prompt()

    base_dir = Path(__file__).resolve().parent
    data_dir = base_dir / "data"

    # フォルダ構成の定義
    racecards_dir = data_dir / "racecards"
    score_factors_dir = data_dir / "ev_factors" / "score_factors"
    prob_factors_dir = data_dir / "ev_factors" / "prob_factors"
    weights_dir = data_dir / "ev_factors" / "weights"
    result_dir = data_dir / "results"

    # フォルダ作成
    for d in [
        racecards_dir,
        score_factors_dir,
        prob_factors_dir,
        weights_dir,
        result_dir,
    ]:
        d.mkdir(parents=True, exist_ok=True)

    racecard_filepath = racecards_dir / f"{race_id}.csv"
    score_filepath = score_factors_dir / f"{race_id}.csv"
    prob_filepath = prob_factors_dir / f"{race_id}.csv"
    weight_filepath = weights_dir / f"{race_id}.csv"
    result_filepath = result_dir / f"{race_id}.csv"

    # --- 1. 出馬表データ ---
    print("出馬表データを確認します：")
    should_fetch_racecard = True
    if racecard_filepath.exists():
        use_existing = input(
            f"{datetime.fromtimestamp(racecard_filepath.stat().st_mtime)}に更新された出馬表データ"
            f" {racecard_filepath} が見つかりました。これを使用しますか？ (Y/n): "
        )
        if use_existing.lower() in ("y", ""):
            print("既存の出馬表データを使用します。")
            df_racecard = pd.read_csv(racecard_filepath)
            should_fetch_racecard = False

    if should_fetch_racecard:
        url = f"https://race.netkeiba.com/odds/index.html?race_id={race_id}"
        print(f"{urlparse(url).netloc}から取得…")
        df_racecard = extract_racecard_from_netkeiba_html(
            fetch_html(url + f"&t={datetime.now().timestamp()}")
        )
        df_racecard.to_csv(racecard_filepath, index=False)

    print(f"\n出馬表:\n{df_racecard[['馬名', 'オッズ']].head()}")
    print()

    # --- 2. 要因データ（スコア/確率） ---
    print("期待値計算要因入力データを確認します：")
    df_ev_score_factors = None
    df_ev_prob_factors = None

    # 既存ファイルの確認
    has_score = score_filepath.exists()
    has_prob = prob_filepath.exists()

    if has_score or has_prob:
        print("既存の要因データが見つかりました。")
        if has_score:
            print(f" - スコア系: {score_filepath}")
        if has_prob:
            print(f" - 確率系: {prob_filepath}")

        if input("これらを使用しますか？ (Y/n): ").lower() in ("y", ""):
            if has_score:
                df_ev_score_factors = pd.read_csv(score_filepath)
            if has_prob:
                df_ev_prob_factors = pd.read_csv(prob_filepath)

    # データが無い場合は新規作成
    if df_ev_score_factors is None and df_ev_prob_factors is None:
        print("データが見つからない、または使用しないため、新規作成します。")
        df_ev_score_factors, df_ev_prob_factors = input_ev_factors_manually(df_racecard)

        # 保存
        if len(df_ev_score_factors.columns) > 1:
            df_ev_score_factors.to_csv(score_filepath, index=False)
            print(f"スコア要因を保存: {score_filepath}")
        if len(df_ev_prob_factors.columns) > 1:
            df_ev_prob_factors.to_csv(prob_filepath, index=False)
            print(f"確率要因を保存: {prob_filepath}")

    # 空のDataFrame対策
    if df_ev_score_factors is None:
        df_ev_score_factors = pd.DataFrame({"馬名": df_racecard["馬名"]})
    if df_ev_prob_factors is None:
        df_ev_prob_factors = pd.DataFrame({"馬名": df_racecard["馬名"]})

    print("\n現在のスコア要因:")
    print(df_ev_score_factors)
    print("\n現在の確率要因:")
    print(df_ev_prob_factors)
    print()

    # --- 3. 重み設定 ---
    ev_factors_weights = {}
    needs_save = False

    # 既存ファイルの読み込み
    if weight_filepath.exists():
        use_existing = input(
            f"重み配分設定 {weight_filepath} が見つかりました。これを使用しますか？ (Y/n): "
        )
        if use_existing.lower() in ("y", ""):
            print("既存の重み設定を使用します。")
            try:
                df_w = pd.read_csv(weight_filepath)
                # 【修正】カラム名を「要因」「重み」に合わせる
                ev_factors_weights = dict(zip(df_w["要因"], df_w["重み"]))
            except Exception as e:
                print(f"ファイルの読み込みに失敗しました: {e}")
                ev_factors_weights = {}
                needs_save = True
        else:
            ev_factors_weights = {}
            needs_save = True
    else:
        needs_save = True

    # 合計計算
    total_weight = sum(ev_factors_weights.values())

    # 対象列リストアップ
    target_columns = []
    target_columns += [c for c in df_ev_score_factors.columns if c != "馬名"]
    target_columns += [c for c in df_ev_prob_factors.columns if c != "馬名"]
    target_columns.append(WIN_RATE_BY_FAVORITE_LABELNAME)

    # 不足分の入力
    for column in target_columns:
        if column in ev_factors_weights:
            print(f"'{column}' の重み: {ev_factors_weights[column]} (設定済み)")
            continue

        needs_save = True
        while True:
            weight_str = input(
                f"期待値計算要因 '{column}' の重みを0.0～1.0の範囲で入力してください (現在の合計: {total_weight:.2f}): "
            )
            if not weight_str:
                weight_str = "0"
            try:
                weight = float(weight_str)
                if 0.0 <= weight <= 1.0 and total_weight + weight <= 1.0 + 1e-9:
                    ev_factors_weights[column] = weight
                    total_weight += weight
                    break
                else:
                    print("無効な重みです。")
            except ValueError:
                print("数値を入力してください。")

    # 残りを人気別勝率へ
    if total_weight < 0.999:
        remaining = 1.0 - total_weight
        print(
            f"残り {remaining:.2f} を{WIN_RATE_BY_FAVORITE_LABELNAME}に割り当てます。"
        )
        ev_factors_weights[WIN_RATE_BY_FAVORITE_LABELNAME] = (
            ev_factors_weights.get(WIN_RATE_BY_FAVORITE_LABELNAME, 0) + remaining
        )
        needs_save = True

    # 保存
    if needs_save:
        print("\n重み設定を保存します...")
        # 【修正】カラム名を「要因」「重み」に合わせる
        df_save = pd.DataFrame(
            list(ev_factors_weights.items()), columns=["要因", "重み"]
        )
        df_save.to_csv(weight_filepath, index=False)
        print(f"保存完了: {weight_filepath}")

    print()

    # --- 4. 計算実行と表示 ---
    df_result = prediction(
        df_racecard, df_ev_score_factors, df_ev_prob_factors, ev_factors_weights
    )

    print("期待値計算結果（内訳付き）：")

    # 表示用カラムの選定
    contribution_cols = [c for c in df_result.columns if c.startswith("寄与_")]
    display_cols = ["馬名", "オッズ"] + contribution_cols + ["統合勝率", "対数期待値", "対数補正オッズ期待値"]

    df_display = df_result[display_cols].copy()

    # パーセント表示化
    for col in contribution_cols + ["統合勝率"]:
        df_display[col] = df_display[col].map(lambda x: f"{x * 100:.2f}%")
    df_display["対数期待値"] = df_display["対数期待値"].map(lambda x: f"{x:.2f}")

    print(df_display)
    df_result.to_csv(result_filepath, index=False)
    df_result.to_html(result_filepath.with_suffix(".html"), index=False)
    print(f"\n結果を保存しました: {result_filepath}")


if __name__ == "__main__":
    main()
