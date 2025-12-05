import sys

from bs4 import BeautifulSoup, Tag
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

def race_date_course_num(html: str) -> tuple[str, str, int]:
    """レース日程(年4桁-月2桁-日2桁)、競馬場、レース番号を取得"""
    soup = BeautifulSoup(html, "html.parser")
    if tag := soup.select_one("a.hit_list_item > div.left"):
        # print("DIVLEFRTTTTT")
        if race_cource_html := tag.select_one(".race_cource"):
            # print("raceCOURSE!!!")
            race_course = race_cource_html.get_text(strip=True)
            race_date_html: Tag = tag.select_one("time.race_date") # type: ignore
            race_date_str = race_date_html.get_text(strip=True)
            # print("置換前：", race_course)
            race_course = race_course.replace(race_date_str, '')
            # print(race_course)
            race_date_str_parts = race_date_str.split("月")
            race_date = str(race_date_html.get("datetime")).split("-")[0] + "-" + race_date_str_parts[0] + "-" + race_date_str_parts[1].split("日")[0]
            # print(race_date)
        if race_num_html := tag.select_one("span.race_num"):
            race_num = int(race_num_html.get_text(strip=True).split("R")[0])
            # print(race_num)
    else:
        print("レース識別データの取得に失敗しました")
        sys.exit(1)
    return race_date, race_course, race_num