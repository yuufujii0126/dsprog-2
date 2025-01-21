import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import sqlite3

def create_suumo_url(base_url, conditions):
    """条件に基づいてURLを生成する関数"""
    url = base_url
    
    # 家賃条件
    if conditions.get('min_rent'):
        url += f"&cb={conditions['min_rent']}"
    if conditions.get('max_rent'):
        url += f"&ct={conditions['max_rent']}"
    
    # 間取り条件
    madori_codes = {
        '1R': 'mdg01', '1K': 'mdg02', '1DK': 'mdg03', '1LDK': 'mdg04',
        '2K': 'mdg05', '2DK': 'mdg06', '2LDK': 'mdg07',
        '3K': 'mdg08', '3DK': 'mdg09', '3LDK': 'mdg10',
        '4K': 'mdg11', '4DK': 'mdg12', '4LDK': 'mdg13'
    }
    
    if conditions.get('madori'):
        for m in conditions['madori']:
            if m in madori_codes:
                url += f"&{madori_codes[m]}=1"
    
    # 専有面積条件
    if conditions.get('min_size'):
        url += f"&mb={conditions['min_size']}"
    if conditions.get('max_size'):
        url += f"&mt={conditions['max_size']}"
    
    return url

def scrape_suumo(url):
    data = []
    page = 1
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    while True:
        try:
            page_url = f"{url}&page={page}"
            response = requests.get(page_url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            items = soup.find_all('div', class_='cassetteitem')
            
            if not items:
                break
                
            for item in items:
                try:
                    # 建物名
                    building_name = item.find('div', class_='cassetteitem_content-title')
                    building_name = building_name.text.strip() if building_name else "情報なし"
                    
                    # 交通情報（駅からの距離）
                    station_div = item.select_one('.cassetteitem_detail-text')
                    station_info = station_div.text.strip() if station_div else "情報なし"
                    
                    # 部屋情報
                    rooms = item.find_all('table', class_='cassetteitem_other')
                    
                    for room in rooms:
                        try:
                            # 家賃
                            rent_element = room.select_one('.cassetteitem_other-emphasis')
                            rent = rent_element.text.strip() if rent_element else "情報なし"
                            
                            # 間取り
                            madori_element = room.select_one('.cassetteitem_madori')
                            floor_plan = madori_element.text.strip() if madori_element else "情報なし"
                            
                            # 面積
                            size_element = room.select_one('.cassetteitem_menseki')
                            size = size_element.text.strip() if size_element else "情報なし"
                            
                            data.append({
                                '建物名': building_name,
                                '駅からの距離': station_info,
                                '家賃': rent,
                                '間取り': floor_plan,
                                '面積': size
                            })
                        except (AttributeError, IndexError) as e:
                            print(f"Error processing room info: {e}")
                            continue
                            
                except Exception as e:
                    print(f"Error processing item: {e}")
                    continue
            
            print(f"Page {page} processed successfully")
            page += 1
            time.sleep(1)
            
        except Exception as e:
            print(f"Error processing page {page}: {e}")
            break
    
    return pd.DataFrame(data)

def analyze_station_distance(df, stations):
    """駅からの距離を分析する関数"""
    station_analysis = []
    for _, row in df.iterrows():
        station_info = row['駅からの距離']
        for station in stations:
            if station in station_info:
                distance = station_info[station_info.find(station):]
                walk_time = ''
                if '徒歩' in distance:
                    walk_time = distance[distance.find('徒歩')+2:distance.find('分')]
                station_analysis.append({
                    '駅名': station,
                    '物件名': row['建物名'],
                    '徒歩分数': walk_time,
                    '家賃': row['家賃']
                })
    return pd.DataFrame(station_analysis)

def save_to_sqlite(df, db_name='suumo_properties.db', table_name='properties'):
    """データをSQLiteデータベースに保存する関数"""
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        create_table_query = f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            building_name TEXT,
            station_distance TEXT,
            rent REAL,
            floor_plan TEXT,
            size REAL
        )
        '''
        cursor.execute(create_table_query)

        df = df.rename(columns={
            '建物名': 'building_name',
            '駅からの距離': 'station_distance',
            '家賃': 'rent',
            '間取り': 'floor_plan',
            '面積': 'size'
        })

        df.to_sql(table_name, conn, if_exists='append', index=False)

        conn.commit()
        conn.close()

        print(f"Data successfully saved to {db_name}, table: {table_name}")
    except Exception as e:
        print(f"Error saving to SQLite: {e}")

# メイン処理
def main():
    # 検索条件の設定
    conditions = {
        'madori': ['ワンルーム', '1K'],  # 希望する間取り
        'max_size': 25,  # 最大面積 (m²)
        'stations': ['大井町', '品川シーサイド', '天王洲アイル', '東京テレポート', '国際展示場']  # フィルタリングしたい駅名
    }

    # 基本となるURL
    base_url = "https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&bs=040&ra=013&cb=0.0&ct=9999999&et=9999999&cn=9999999&mb=0&mt=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&fw2=&ek=009014660&ek=009025630&ek=009025440&ek=009053940&ek=009005480&rn=0090"

    # URLの生成とスクレイピング
    search_url = create_suumo_url(base_url, conditions)
    df = scrape_suumo(search_url)

    if not df.empty:
        try:
            # 数値データの整形
            df['家賃'] = df['家賃'].replace('情報なし', '0')
            df['家賃'] = df['家賃'].str.replace('万円', '').astype(float)
            
            df['面積'] = df['面積'].replace('情報なし', '0')
            df['面積'] = df['面積'].str.replace('m2', '').astype(float)
            
            # 駅名でフィルタリング
            if 'stations' in conditions:
                station_filter = df['駅からの距離'].apply(
                    lambda x: any(station in x for station in conditions['stations'])
                )
                df = df[station_filter]
            
            # その他の条件でフィルタリング
            df = df[
                (df['間取り'].isin(conditions['madori'])) &
                (df['面積'] <= conditions['max_size'])
            ]
            
            # 結果をCSVファイルとして保存
            df.to_csv('suumo_filtered_properties.csv', index=False, encoding='utf-8-sig')
            
            # 結果の表示
            print("\nFirst 5 rows of the filtered data:")
            print(df.head())
            print(f"\nTotal number of properties matching criteria: {len(df)}")
            
            # 駅ごとの物件数を表示
            print("\nProperties count by station:")
            station_counts = df['駅からの距離'].apply(
                lambda x: next((station for station in conditions['stations'] if station in x), 'Other')
            ).value_counts()
            print(station_counts)
            
            # 駅からの距離の分析
            station_analysis_df = analyze_station_distance(df, conditions['stations'])
            print("\nStation Distance Analysis:")
            print(station_analysis_df.head())
            
            # 統計情報の表示
            print("\nSummary Statistics:")
            print(df.describe())
            
            # SQLiteデータベースに保存
            save_to_sqlite(df)
            
        except Exception as e:
            print(f"Error processing final data: {e}")
    else:
        print("No data was collected")

if __name__ == "__main__":
    main()