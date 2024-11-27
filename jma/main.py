import flet as ft
import requests
import json
import logging

# デバッグログの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeatherApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "天気予報アプリ"
        self.page.window_width = 800
        self.page.window_height = 600

        # 最新のAPIエンドポイント
        self.AREAS_URL = "https://www.jma.go.jp/bosai/common/const/area.json"
        self.FORECAST_BASE_URL = "https://www.jma.go.jp/bosai/forecast/data/forecast/"

        # 状態変数
        self.areas = {}
        self.selected_area_code = None

        # UIコンポーネントの作成
        self.rail = self._create_navigation_rail()
        self.area_dropdown = self._create_area_dropdown()
        self.forecast_display = self._create_forecast_display()

        # 初期セットアップ
        self._load_areas()
        self._setup_layout()

    def _load_areas(self):
        """地域リストをAPIから読み込む"""
        try:
            response = requests.get(self.AREAS_URL)
            response.raise_for_status()
            all_areas = response.json()
            
            # デバッグ用：全地域コードと地域名を出力
            logger.info("利用可能な地域コード:")
            for code, area in all_areas['offices'].items():
                logger.info(f"コード: {code}, 地域名: {area['name']}")
            
            # 地域リストの作成
            self.areas = {
                code: area['name'] 
                for code, area in all_areas['offices'].items()
            }
            
            # ドロップダウンの更新
            self.area_dropdown.options = [
                ft.dropdown.Option(key=code, text=name) 
                for code, name in self.areas.items()
            ]
        except Exception as e:
            logger.error(f"地域リストの読み込みに失敗しました: {e}")
            self.forecast_display.controls[0].value = f"エラー: {e}"
            self.forecast_display.update()

    def _fetch_forecast(self, area_code):
        """指定された地域の天気予報を取得"""
        try:
            # 完全なURLをログに出力
            url = f"{self.FORECAST_BASE_URL}{area_code}.json"
            logger.info(f"フォーキャストURL: {url}")

            response = requests.get(url)
            logger.info(f"ステータスコード: {response.status_code}")
            logger.info(f"レスポンスヘッダー: {response.headers}")

            response.raise_for_status()
            forecast_data = response.json()

            # デバッグ用：JSONデータの詳細出力
            logger.info("APIレスポンス:")
            logger.info(json.dumps(forecast_data, indent=2, ensure_ascii=False))

            forecast_text = self._format_forecast(forecast_data)
            
            self.forecast_display.controls[0].value = forecast_text
            self.forecast_display.update()

        except requests.exceptions.RequestException as e:
            logger.error(f"リクエストエラー: {e}")
            self.forecast_display.controls[0].value = f"通信エラー: {e}"
            self.forecast_display.update()

    def _format_forecast(self, forecast_data):
        """予報データを読みやすいテキストに整形"""
        try:
            # データの存在と形式を確認
            if not forecast_data or not isinstance(forecast_data, list):
                return "予報データの形式が異常です"

            # 最初のデータセットを使用
            area_forecast = forecast_data[0]
            
            # レポート名の取得
            location = area_forecast.get('reportName', '不明な地域')
            
            # 時系列データの抽出
            time_series = area_forecast.get('timeSeries', [])
            if not time_series:
                return "予報データに時系列情報がありません"

            # 予報テキストの作成
            forecast_text = f"地域: {location}\n\n天気予報:\n"
            
            # 最初の時系列から天気情報を抽出
            first_time_series = time_series[0]
            areas = first_time_series.get('areas', [])
            
            if areas:
                first_area = areas[0]
                weathers = first_area.get('weathers', [])
                
                for i, weather in enumerate(weathers, 1):
                    forecast_text += f"第{i}期間: {weather}\n"
            
            # 気温情報の抽出（存在する場合）
            if len(time_series) > 2:
                temp_series = time_series[2]
                temp_areas = temp_series.get('areas', [])
                
                if temp_areas:
                    first_temp_area = temp_areas[0]
                    temps = first_temp_area.get('temps', [])
                    
                    forecast_text += "\n気温:\n"
                    for i, temp in enumerate(temps, 1):
                        forecast_text += f"第{i}期間: {temp}°C\n"
            
            return forecast_text

        except Exception as e:
            logger.error(f"予報情報の解析に失敗しました: {e}")
            return f"予報情報の解析に失敗しました: {e}"

    def _create_navigation_rail(self):
        """ナビゲーションレールの作成"""
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
        """地域選択ドロップダウンの作成"""
        dropdown = ft.Dropdown(
            width=300,
            hint_text="地域を選択",
            on_change=self._on_area_select
        )
        return dropdown

    def _create_forecast_display(self):
        """天気予報表示エリアの作成"""
        return ft.Column([
            ft.Text("地域を選択してください", size=16),
        ])

    def _on_area_select(self, e):
        """地域選択イベントの処理"""
        self.selected_area_code = e.control.value
        if self.selected_area_code:
            self._fetch_forecast(self.selected_area_code)

    def _setup_layout(self):
        """メインアプリケーションレイアウトの設定"""
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