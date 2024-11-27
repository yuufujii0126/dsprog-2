import flet as ft
import requests
import json

class WeatherApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "天気予報アプリ"
        self.page.window_width = 800
        self.page.window_height = 600

        # Areas JSON URL
        self.AREAS_URL = "http://www.jma.go.jp/bosai/common/const/area.json"
        
        # Forecast base URL
        self.FORECAST_BASE_URL = "https://www.jma.go.jp/bosai/forecast/data/forecast/"

        # State variables
        self.areas = {}
        self.selected_area_code = None

        # UI Components
        self.rail = self._create_navigation_rail()
        self.area_dropdown = self._create_area_dropdown()
        self.forecast_display = self._create_forecast_display()

        # Initial setup
        self._load_areas()
        self._setup_layout()

    def _load_areas(self):
        """Load area list from JMA API"""
        try:
            response = requests.get(self.AREAS_URL)
            response.raise_for_status()
            all_areas = response.json()
            
            # Filter and organize areas
            self.areas = {
                code: area['name'] 
                for code, area in all_areas['offices'].items()
            }
            
            # Update dropdown with areas
            self.area_dropdown.options = [
                ft.dropdown.Option(key=code, text=name) 
                for code, name in self.areas.items()
            ]
        except Exception as e:
            print(f"地域リストの読み込みに失敗しました: {e}")
            self.forecast_display.controls[0].value = f"エラー: {e}"
            self.forecast_display.update()

    def _fetch_forecast(self, area_code):
        """Fetch weather forecast for specific area"""
        try:
            url = f"{self.FORECAST_BASE_URL}{area_code}.json"
            response = requests.get(url)
            response.raise_for_status()
            forecast_data = response.json()

            # Extract relevant forecast information
            forecast_text = self._format_forecast(forecast_data)
            
            # Update display
            self.forecast_display.controls[0].value = forecast_text
            self.forecast_display.update()

        except Exception as e:
            print(f"天気予報の取得に失敗しました: {e}")
            self.forecast_display.controls[0].value = f"エラー: {e}"
            self.forecast_display.update()

    def _format_forecast(self, forecast_data):
        """Format forecast data into readable text"""
        try:
            # Get first area's forecast (typically most detailed)
            area_forecast = forecast_data[0]
            
            # Extract key forecast details
            location = area_forecast['reportName']
            weather_info = area_forecast['timeSeries'][0]['areas'][0]
            
            # Construct forecast text
            forecast_text = f"地域: {location}\n\n"
            forecast_text += "天気予報:\n"
            for i, weather in enumerate(weather_info['weathers'], 1):
                forecast_text += f"第{i}期間: {weather}\n"
            
            forecast_text += "\n気温:\n"
            for i, temp in enumerate(area_forecast['timeSeries'][2]['areas'][0]['temps'], 1):
                forecast_text += f"第{i}期間: {temp}°C\n"
            
            return forecast_text

        except Exception as e:
            return f"予報情報の解析に失敗しました: {e}"

    def _create_navigation_rail(self):
        """Create navigation rail"""
        return ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.icons.HOME_OUTLINED,
                    selected_icon=ft.icons.HOME,
                    label="天気予報"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.SETTINGS_OUTLINED,
                    selected_icon=ft.icons.SETTINGS,
                    label="設定"
                ),
            ]
        )

    def _create_area_dropdown(self):
        """Create area selection dropdown"""
        dropdown = ft.Dropdown(
            width=300,
            hint_text="地域を選択",
            on_change=self._on_area_select
        )
        return dropdown

    def _create_forecast_display(self):
        """Create forecast display area"""
        return ft.Column([
            ft.Text("地域を選択してください", size=16),
        ])

    def _on_area_select(self, e):
        """Handle area selection event"""
        self.selected_area_code = e.control.value
        if self.selected_area_code:
            self._fetch_forecast(self.selected_area_code)

    def _setup_layout(self):
        """Set up main application layout"""
        self.page.add(
            ft.Row([
                self.rail,
                ft.VerticalDivider(width=1),
                ft.Column([
                    ft.Text("地域を選択", size=20, weight=ft.FontWeight.BOLD),
                    self.area_dropdown,
                    self.forecast_display
                ], expand=True),
            ], expand=True)
        )

def main(page: ft.Page):
    WeatherApp(page)

ft.app(main)