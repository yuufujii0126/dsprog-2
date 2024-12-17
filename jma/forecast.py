import sqlite3
import json
import requests

# JSONファイルのパス
json_file = "/Users/fujiiyuu/dsprog-2/jma/response.json"

def get_area_codes(data):
    area_codes = []
    
    # officesから直接コードを取得
    if 'offices' in data:
        # officesのキー（コード）を直接リストに追加
        area_codes.extend(list(data['offices'].keys()))
    
    # 重複を削除
    area_codes = list(set(area_codes))
    return area_codes

def generate_weather_urls(area_codes):
    base_url = "https://www.jma.go.jp/bosai/forecast/data/forecast/{}.json"
    urls = []
    for code in area_codes:
        # 6桁のコードのみを使用（気象情報取得用）
        if len(code) == 6:
            urls.append(base_url.format(code))
    return urls

def create_database():
    conn = sqlite3.connect('forecast.db')
    cursor = conn.cursor()

    # forecastテーブルの作成
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS forecast (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            areacode TEXT NOT NULL,
            areaname TEXT NOT NULL,
            date TEXT NOT NULL,
            weather TEXT,
            maxtemp REAL,
            mintemp REAL
        )
    ''')

    conn.commit()
    return conn, cursor

def insert_weather_data(conn, cursor, data):
    try:
        if isinstance(data, list):
            # 最初のデータセット（今日・明日・明後日の予報）を処理
            forecast = data[0]  # 最初の予報データのみを使用
            publishing_office = forecast.get('publishingOffice', '')
            report_datetime = forecast.get('reportDatetime', '')
            time_series_list = forecast.get("timeSeries", [])

            weather_data = {}  # 地域ごとの天気データを格納する辞書

            # 天気情報の処理（最初のtimeSeries）
            if time_series_list and len(time_series_list) > 0:
                weather_series = time_series_list[0]
                weather_times = weather_series.get("timeDefines", [])
                for area in weather_series.get("areas", []):
                    area_code = area["area"]["code"]
                    weather_data[area_code] = {
                        "name": area["area"]["name"],
                        "weathers": area.get("weathers", []),
                        "times": weather_times
                    }

            # データベースに挿入
            for area_code, area_data in weather_data.items():
                area_name = area_data["name"]
                weathers = area_data.get("weathers", [])
                temps = area_data.get("temps", [])
                times = area_data.get("times", [])

                # 今日・明日・明後日のデータのみを処理
                for i in range(min(3, len(times))):
                    weather = weathers[i] if i < len(weathers) else None
                    temp = temps[i] if i < len(temps) else None

                    cursor.execute('''
                        INSERT INTO forecast 
                        (areacode, areaname, date, weather, maxtemp, mintemp)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        area_code,
                        area_name,
                        times[i],
                        weather,
                        float(temp) if temp not in [None, ''] else None,
                        None
                    ))

        conn.commit()
        print("天気データの挿入が完了しました！")

    except Exception as e:
        print(f"データ挿入中にエラーが発生しました: {e}")
        print("エラーの詳細:", str(e))
        conn.rollback()

def main():
    try:
        # JSONファイルを読み込む
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # エリアコードを取得
        area_codes = get_area_codes(data)

        # 天気情報のURLを生成
        urls = generate_weather_urls(area_codes)

        # データベースの作成と接続
        conn, cursor = create_database()

        # 各URLから天気データを取得し、データベースに挿入
        for url in urls:
            print(f"データ取得中: {url}")
            response = requests.get(url)
            if response.status_code == 200:
                weather_data = response.json()
                insert_weather_data(conn, cursor, weather_data)
            else:
                print(f"データ取得に失敗しました: {url}")

        print("すべての処理が完了しました！")

    except Exception as e:
        print(f"エラーが発生しました: {e}")

    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()