import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def create_suumo_url(base_url, conditions):
    """条件に基づいてURLを生成する関数"""
    url = base_url
    
    # 間取り条件
    if conditions.get('madori'):
        for m in conditions['madori']:
            url += f"&mt={m}"
    
    # 専有面積条件
    if conditions.get('max_size'):
        url += f"&mt={conditions['max_size']}"

    # 築年数条件
    if conditions.get('building_age'):
        age = conditions['building_age']
        if age.get('min'):
            url += f"&mb={age['min']}"
        if age.get('max'):
            url += f"&mt={age['max']}"
    
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
            print(f"Scraping URL: {page_url}")
            
            response = requests.get(page_url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            items = soup.find_all('div', class_='cassetteitem')
            
            if not items:
                print(f"No items found on page {page}")
                break
                
            for item in items:
                try:
                    # 建物名
                    building_name = item.find('div', class_='cassetteitem_content-title')
                    building_name = building_name.text.strip() if building_name else "情報なし"
                    
                    # 交通情報
                    station_div = item.select_one('.cassetteitem_detail-text')
                    station_info = station_div.text.strip() if station_div else "情報なし"
                    
                    # 部屋情報
                    rooms = item.find_all('table', class_='cassetteitem_other')

                    # 築年数
                    year_div = item.select_one('.cassetteitem_detail-col3')
                    year = year_div.text.strip() if year_div else "情報なし"
                
                    
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
                                '駅情報': station_info,
                                '家賃': rent,
                                '間取り': floor_plan,
                                '面積': size,
                                '築年数': year
                            })
                            print(f"Added property: {building_name}")
                            
                        except Exception as e:
                            print(f"Error processing room: {e}")
                            continue
                            
                except Exception as e:
                    print(f"Error processing item: {e}")
                    continue
            
            print(f"Page {page} processed successfully")
            page += 1
            time.sleep(2)
            
        except Exception as e:
            print(f"Error processing page {page}: {e}")
            break
    
    return pd.DataFrame(data)

# 基本となるURL（指定された5駅を含む）
base_url = "https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&bs=040&ra=013&cb=0.0&ct=9999999&et=9999999&cn=9999999&mb=0&mt=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&fw2=&ek=009014660&ek=009025630&ek=009025440&ek=009053940&ek=009005480&rn=0090"

# 検索条件の設定
conditions = {
    'madori': ['ワンルーム', '1K'],
    'max_size': 25,
    'year': {
        'min': 0,
        'max': 15
    }
}

# 条件を適用したURLの生成
search_url = create_suumo_url(base_url, conditions)

print(f"Generated URL: {search_url}")

# スクレイピングの実行
df = scrape_suumo(search_url)

# データが空でないことを確認
if not df.empty:
    try:
        # 数値データの整形
        df['家賃'] = df['家賃'].replace('情報なし', '0')
        df['家賃'] = df['家賃'].str.replace('万円', '').astype(float)
        
        df['面積'] = df['面積'].replace('情報なし', '0')
        df['面積'] = df['面積'].str.replace('m2', '').astype(float)

        df['築年数'] = df['築年数'].replace('情報なし', '0')
        df['築年数'] = df['築年数'].str.replace('新築', '0')
        df['築年数'] = df['築年数'].str.replace('築', '')
        df['築年数'] = df['築年数'].str.replace('年', '').astype(float)

        
        # 結果をCSVファイルとして保存
        df.to_csv('suumo_filtered_properties.csv', index=False, encoding='utf-8-sig')
        
        # 結果の表示
        print("\nFirst 5 rows of the filtered data:")
        print(df.head())
        print(f"\nTotal number of properties matching criteria: {len(df)}")
        
        # 統計情報の表示
        print("\nSummary Statistics:")
        print(df.describe())
        
    except Exception as e:
        print(f"Error processing final data: {e}")
else:
    print("No data was collected")