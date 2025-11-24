import sys
import re

from bs4 import BeautifulSoup
import numpy as np
import pandas as pd


def racecard(html: str) -> pd.DataFrame:
    """
    馬名,オッズ,人気を列とする形式の出馬表をhtmlから取得する。
    """
    soup = BeautifulSoup(html, "html.parser")
    html_table = soup.find("table", {"class": "RaceOdds_HorseList_Table"})
    df = pd.DataFrame()
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
        df = pd.concat([df, pd.DataFrame([row_data])], ignore_index=True)
    df["オッズ"] = pd.to_numeric(df["オッズ"], errors="coerce")
    df["人気"] = range(1, len(df) + 1)
    return df
