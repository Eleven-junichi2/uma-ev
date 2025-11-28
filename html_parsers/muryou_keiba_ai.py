import sys

from bs4 import BeautifulSoup
import pandas as pd


def ai_prediction_card(html: str) -> pd.DataFrame:
    """
    馬名,無料競馬AI予想指数を列とする形式の出馬表をhtmlから取得する。
    """
    soup = BeautifulSoup(html, "html.parser")
    html_table = soup.select_one("table.race_table > tbody")
    if html_table is None:
        print("データ取得先のテーブルが見つかりませんでした。")
        print("URLが正しいか確認してください。")
        sys.exit(1)
    # print(html_table)
    horses = []
    for html_row in html_table.find_all("tr"):
        # print(html_row)
        cells = html_row.find_all("td")
        if tag := cells[1].select_one("a.bamei"):
            horse_name = tag.get_text(strip=True)
        else:
            horse_name = None
        if tag := cells[3].select_one("span.predict"):
            ai_prediction = tag.get_text(strip=True)
        horses.append({"馬名": horse_name, "無料競馬AI予想指数": ai_prediction})
    df = pd.DataFrame(horses)
    df["無料競馬AI予想指数"] = pd.to_numeric(df["無料競馬AI予想指数"], errors="coerce")
    return df
