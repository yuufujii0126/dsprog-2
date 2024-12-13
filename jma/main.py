import flet as ft
import requests
import json
from datetime import datetime

class WeatherApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "日本の天気予報"
        self.page.window_width = 800
        self.page.window_height = 800
        
        # URLs
        self.AREAS_URL = "https://www.jma.go.jp/bosai/common/const/area.json"
        self.FORECAST_BASE_URL = "https://www.jma.go.jp/bosai/forecast/data/forecast/"
        
        # UI Components
        self.area_dropdown = ft.Dropdown(
            width=400,
            label="地域を選択してください",
            on_change=self.on_area_selected
        )
        
        self.weather_display = ft.Column(
            controls=[
                ft.Text("天気予報", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("地域を選択してください", size=16),
            ],
            scroll=ft.ScrollMode.AUTO,
        )
        
        self.setup_page()
        self.load_areas()
    
    def setup_page(self):
        self.page.add(
            ft.Container(
                content=ft.Column([
                    ft.Row([self.area_dropdown], alignment=ft.MainAxisAlignment.CENTER),
                    self.weather_display
                ]),
                padding=20
            )
        )
    
    def format_date(self, dt_str):
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return dt.strftime('%Y年%m月%d日')
    
    def load_areas(self):
        try:
            response = requests.get(self.AREAS_URL)
            areas_data = response.json()
            
            self.area_dropdown.options = [
                ft.dropdown.Option(
                    key=code,
                    text=f"{data['name']} ({data['officeName']})"
                )
                for code, data in areas_data['offices'].items()
            ]
            
            self.area_dropdown.options.sort(key=lambda x: x.text)
            self.page.update()
            
        except Exception as e:
            print(f"地域データ読み込みエラー: {e}")
            self.weather_display.controls = [
                ft.Text("地域データの読み込みに失敗しました", color="red")
            ]
            self.page.update()
    
    def create_daily_forecast_container(self, date, forecasts):
        return ft.Container(
            content=ft.Column([
                ft.Text(date, size=18, weight=ft.FontWeight.BOLD),
                *forecasts
            ]),
            padding=10,
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=10,
            margin=ft.margin.only(top=10)
        )

    def on_area_selected(self, e):
        selected_code = e.control.value
        if not selected_code:
            return
        
        try:
            forecast_url = f"{self.FORECAST_BASE_URL}{selected_code}.json"
            response = requests.get(forecast_url)
            forecast_data = response.json()
            
            # 表示をクリア
            self.weather_display.controls = [
                ft.Text("天気予報", size=24, weight=ft.FontWeight.BOLD),
                ft.Text(f"選択地域: {e.control.options[e.control.options.index(next(opt for opt in e.control.options if opt.key == selected_code))].text}",
                       size=18, weight=ft.FontWeight.BOLD)
            ]
            
            # 日付ごとの予報データを格納する辞書
            daily_forecasts = {}
            
            # 予報データの処理
            for report in forecast_data:
                for time_series in report['timeSeries']:
                    if 'areas' in time_series and time_series['areas']:
                        area = time_series['areas'][0]
                        time_defines = [self.format_date(td) for td in time_series['timeDefines']]
                        
                        for i, date_str in enumerate(time_defines):
                            if date_str not in daily_forecasts:
                                daily_forecasts[date_str] = []
                            
                            forecast_info = []
                            
                            # 天気の情報
                            if 'weathers' in area and i < len(area['weathers']):
                                forecast_info.append(f"天気: {area['weathers'][i]}")
                            
                            # 風の情報
                            if 'winds' in area and i < len(area['winds']):
                                forecast_info.append(f"風: {area['winds'][i]}")
                            
                            # 波の情報
                            if 'waves' in area and i < len(area['waves']):
                                forecast_info.append(f"波: {area['waves'][i]}")
                            
                            if forecast_info:
                                daily_forecasts[date_str].append(
                                    ft.Text(f"{' / '.join(forecast_info)}")
                                )
            
            # 日付ごとにまとめて表示
            for date, forecasts in sorted(daily_forecasts.items()):
                if forecasts:  # 予報がある場合のみ表示
                    self.weather_display.controls.append(
                        self.create_daily_forecast_container(date, forecasts)
                    )
            
            self.page.update()
            
        except Exception as e:
            print(f"天気予報取得エラー: {e}")
            self.weather_display.controls = [
                ft.Text("天気予報の取得に失敗しました", color="red")
            ]
            self.page.update()

def main(page: ft.Page):
    page.title = "天気予報アプリ"
    WeatherApp(page)

ft.app(target=main)