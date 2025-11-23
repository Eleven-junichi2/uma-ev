from __init__ import parser_finder
from odds2ev.scraping import fetch_html


if __name__ == "__main__":
    race_id = input("netkeibaレースidを入力してください：")
    url = fr"https://race.netkeiba.com/odds/index.html?race_id={race_id}"
    if parser := parser_finder.find(url):
        racecard = parser(fetch_html(url))
    print(racecard)