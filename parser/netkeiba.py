import sys
import re

from bs4 import BeautifulSoup
import numpy as np
import pandas as pd


def racecard(html: str) -> pd.DataFrame:
    soup = BeautifulSoup(html, "html.parser")
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
