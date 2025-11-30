import sys
import re

from bs4 import BeautifulSoup
import pandas as pd


def odds(html: str) -> pd.DataFrame:
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


def raceinfo(html: str) -> dict:
    """
    距離,馬場種別,馬場状態等を格納するdictをhtmlから取得する。
    """
    soup = BeautifulSoup(html, "html.parser")
    track_condition = None
    if tag := soup.select_one("div.RaceData01 > span.Item03"):
        track_condition = tag.get_text(strip=True).split(":")[1]
    # if tag := soup.select_one("div.RaceData01"):
    # print(tag.get_text(strip=True))
    return {"馬場状態": track_condition}


def racecard(html: str) -> pd.DataFrame:
    """
    馬名,性別,馬齢,斤量,馬体重,馬体重増減,枠,馬番,騎手,厩舎,オッズ,人気を列とする形式の出馬表をhtmlから取得する。
    """
    soup = BeautifulSoup(html, "html.parser")
    html_table = soup.select_one("table.Shutuba_Table > tbody")
    horses = []
    if html_table is None:
        print("データ取得先のテーブルが見つかりませんでした。")
        print("URLやレースIDが正しいか確認してください。")
        sys.exit(1)
    for html_row in html_table.find_all("tr", {"class": "HorseList"}):
        cells = html_row.find_all("td")
        horse_name = cells[3].get_text(strip=True)
        odds = cells[9].get_text(strip=True)
        gender_and_age = cells[4].get_text(strip=True)
        gender = gender_and_age[0]
        age = gender_and_age[1:]
        impost = cells[5].get_text(strip=True)  # 斤量を取得
        weight_and_change = cells[8].get_text(strip=True)
        if weight_and_change and weight_and_change != "--":
            # 取り消しで"--"が馬体重セルに入るので条件分岐で対策
            weight, weight_change = weight_and_change.split("(")
            weight_change = weight_change[:-1]
        else:
            weight = None
            weight_change = None
        bracket_num = cells[0].get_text(strip=True)
        horse_num = cells[1].get_text(strip=True)
        jockey = cells[6].get_text(strip=True)
        trainer = cells[7].get_text(strip=True)
        popularity = cells[10].get_text(strip=True)
        horses.append(
            {
                "馬名": horse_name,
                "性別": gender,
                "馬齢": age,
                "斤量": impost,
                "馬体重": weight,
                "馬体重増減": weight_change,
                "枠番": bracket_num,
                "馬番": horse_num,
                "騎手": jockey,
                "厩舎": trainer,
                "オッズ": odds,
                "人気": popularity,
            }
        )
    df = pd.DataFrame(horses)
    if not df.empty:
        str_cols = ["馬名", "性別", "騎手", "厩舎"]
        for col in df.columns:
            if col in str_cols:
                continue
            # errors='coerce' なので、"取消" などの文字は自動的に NaN になります
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.sort_values("人気", ignore_index=True)
    return df


def race_date_to_race_id(html: str) -> dict:
    calendar = {}
    soup = BeautifulSoup(html, "html.parser")
    date_pattern = re.compile(r"(\d+)年(\d+)月(\d+)日")
    date = None
    if tag := soup.select_one("title"):
        title = tag.get_text(strip=True)
        if match := date_pattern.search(title):
            year, month, day = match.groups()
            date = f"{year}-{month}-{day}"
            calendar[date] = {}
    racecourse_pattern = re.compile(r"\d+回(.+)\d+日目")
    racecourse = None
    race_id_url_pattern = re.compile(r"race_id=(\d+)")
    for dl in soup.select("dl.RaceList_DataList"):
        if datatitle := dl.select_one("p.RaceList_DataTitle"):
            if match := racecourse_pattern.match(datatitle.get_text(strip=True)):
                racecourse = match.group(1)
                calendar[date][racecourse] = {}
        for li in dl.select("ul li"):
            if tag := li.select_one("div.Race_Num"):
                race_num = int(tag.get_text(strip=True).replace("R", ""))
                calendar[date][racecourse][race_num] = None
            if a := li.select_one("a"):
                race_id_url = str(a.get("href"))
                if match := race_id_url_pattern.search(race_id_url):
                    race_id = match.group(1)
                    calendar[date][racecourse][race_num] = race_id
    return calendar


def name_to_horse_id_from_racecard(html) -> dict:
    name_to_horse_id = {}
    soup = BeautifulSoup(html, "html.parser")
    html_table = soup.select_one("table.Shutuba_Table > tbody")
    if html_table is None:
        print("データ取得先のテーブルが見つかりませんでした。")
        print("URLやレースIDが正しいか確認してください。")
        sys.exit(1)
    for html_row in html_table.find_all("tr", {"class": "HorseList"}):
        cells = html_row.find_all("td")
        horse_name = cells[3].get_text(strip=True)
        if tag := cells[3].select_one("a"):
            id = str(tag.get("href")).split("/")[-1]
        name_to_horse_id[horse_name] = id
    return name_to_horse_id


def pedigree(html) -> dict:
    # pedigree_df = pd.DataFrame()
    pedigree_data = {"馬名": "", "父": "", "母父": "", "父父": ""}
    soup = BeautifulSoup(html, "html.parser")
    # print(soup)
    if html_table := soup.select_one("table.blood_table > tbody"):
        cells = html_table.select("tr td")
        for (i, tag), family in zip(
            enumerate(cells),
            (
                "父",
                "父父",
                "父父父",
                "父父父父",
                "父父父父父",
                "父父父父母",
                "父父父母",
                "父父父母父",
                "父父父母母",
                "父父母",
                "父父母父",
                "父父母父父",
                "父父母父母",
                "父父母母",
                "父父母母父",
                "父父母母母",
                "父母",
                "父母父",
                "父母父父",
                "父母父父父",
                "父母父父母",
                "父母父母",
                "父母父母父o",
                "父母父母母",
                "父母母",
                "父母母父",
                "父母母父父",
                "父母母父母",
                "父母母母",
                "父母母母父",
                "父母母母母",
                "母",
                "母父",
                "母父父",
                "母父父父",
                "母父父父父",
                "母父父父母",
                "母父父母",
                "母父父母父",
                "母父父母母",
                "母父母",
                "母父母父",
                "母父母父父",
                "母父母父母",
                "母父母母",
                "母父母母父",
                "母父母母母",
                "母母",
                "母母父",
                "母母父父",
                "母母父父父",
                "母母父父母",
                "母母父母",
                "母母父母父",
                "母母父母母",
                "母母母",
                "母母母父",
                "母母母父父",
                "母母母父母",
                "母母母母",
                "母母母母父",
                "母母母母母",
            ),
        ):
            if horse := tag.select_one("a"):
                name = horse.get_text().split("\n")[0].strip()
                pedigree_data[family] = name
    else:
        print("データ取得先のテーブルが見つかりませんでした。")
        print("URLやレースID、プログラムが正しいか確認してください。")
        sys.exit(1)
    if tag := soup.select_one("div.horse_title h1"):
        pedigree_data["馬名"] = tag.get_text(strip=True)
    # print(pedigree_data)
    return pedigree_data
