import requests
from bs4 import BeautifulSoup

def fetch_single_horse_data(url):
    """
    Netkeibaの単勝オッズページから、ID='ninki-data-1' のtrタグの内容を抽出します。
    """
    # URLに単勝オッズのパラメータ '&type=b1' を確実に追加
    target_url = url
    if "&type=b1" not in target_url:
        target_url += "&type=b1" if "?" in target_url else "?type=b1"
    
    print(f"✅ URL: {target_url} からデータを取得しています...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # ページにアクセス
        response = requests.get(target_url, headers=headers, timeout=10)
        response.raise_for_status() 
        
    except requests.exceptions.RequestException as e:
        print(f"❌ データの取得中にエラーが発生しました: {e}")
        return

    # HTMLをBeautifulSoupで解析
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # ★ 最小目標: ID='ninki-data-1' の<tr>タグを直接検索 ★
    target_row = soup.find('tr', id='ninki-data-1')
    
    if target_row is None:
        print("⚠️ ID='ninki-data-1' のデータ行が見つかりませんでした。")
        return

    print("\n--- 🐴 ID='ninki-data-1' のデータ行の内容 ---")
    
    # <tr>タグ内のすべての<td>要素を取得
    cols = target_row.find_all('td')
    
    print(f"取得した <td> 要素の数: {len(cols)}")
    
    # 各<td>要素の内容をインデックス付きで出力
    for i, col in enumerate(cols):
        # 要素内の改行やスペースを削除して内容を表示
        content = col.text.strip().replace('\n', ' ').replace('  ', ' ')
        print(f"  [{i}|{col.get("class")}]: {content}")

# class NetkeibaScraper:
#     """
#     Netkeibaの予想オッズページからデータを抽出するクラス。
#     """
#     def __init__(self, race_id):
#         self.base_url = base_url
    
#     def fetch_odds_card(self):
#         """
#         指定されたURLからデータを取得し、ID='ninki-data-1' の<tr>タグの内容を抽出します。
#         """
#         fetch_single_horse_data(self.base_url)

# --- 実行部分 ---
if __name__ == "__main__":
    print("--- 🐴 最小限のデバッグプログラム ---")
    
    target_url = input("予想オッズメニューのURLを入力してください: ")
    
    if not target_url:
        print("URLが入力されませんでした。プログラムを終了します。")
    else:
        fetch_single_horse_data(target_url)