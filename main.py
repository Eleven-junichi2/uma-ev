import re
import sys

from bs4 import BeautifulSoup
import numpy as np
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import pandas as pd


def fetch_html(url: str) -> str:
    driver_options = Options()
    driver_options.add_argument("--headless")
    try:
        driver = webdriver.Firefox(options=driver_options)
        driver.implicitly_wait(5)
        driver.get(url)
        html_data = driver.page_source
    finally:
        driver.quit()
    return html_data


def dataframe_from_html(html_data: str) -> pd.DataFrame:
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
                row_data[htmlclass2field[class_]] = data.get_text()
        dataframe = pd.concat([dataframe, pd.DataFrame([row_data])], ignore_index=True)
    dataframe["オッズ"] = pd.to_numeric(dataframe["オッズ"], errors="coerce")
    return dataframe

def scraping_prompt() -> pd.DataFrame:
    if len(sys.argv) < 2:
        race_id = input("レースIDを入力してください (例: 202505050611): ")
        if race_id == "":
            race_id = "202505050611"
    url = f"https://race.netkeiba.com/odds/index.html?race_id={race_id}"
    dataframe = dataframe_from_html(fetch_html(url))
    dataframe.to_csv(f"{race_id}.csv", index=False)
    return dataframe

def main():
    # TODO: すでにcsvが存在する場合は、存在するリストを表示して選択できるようにする。読み込む時、更新するかどうかも選択できるようにする。
    dataframe = scraping_prompt()
    print(
        dataframe.sort_values(
            "オッズ",
            ascending=True,
        )
    )
    dataframe["評価点"] = np.nan
    dataframe["期待値"] = np.nan
    print()
    for idx, row in dataframe.iterrows():
        score = float(input(f"{row['馬名']}の評価点: "))
        dataframe.at[idx, "評価点"] = score  # type: ignore
    print()
    for idx, row in dataframe.iterrows():
        if row["オッズ"] > 0:
            expected_value = row["オッズ"] * row["評価点"] / dataframe["評価点"].sum()
            dataframe.at[idx, "期待値"] = expected_value  # type: ignore
    print(dataframe.sort_values("期待値", ascending=False))


if __name__ == "__main__":
    main()