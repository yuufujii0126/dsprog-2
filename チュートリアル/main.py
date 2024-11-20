import flet as ft

def main(page: ft.Page):
    page.title = "Flet counter example"
    # パーツの配置を決定
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # テキストフィールドを作成、初期位置を設定
    txt_number = ft.TextField(value="0", text_align=ft.TextAlign.RIGHT, width=100)

    # テキストを減らす関数、増やす関数
    def minus_click(e):
        txt_number.value = str(int(txt_number.value) - 1)
        page.update()

    def plus_click(e):
        txt_number.value = str(int(txt_number.value) + 1)
        page.update()

    page.add(
        # 横並びに配置するコマンド
        ft.Row(
            [
                ft.IconButton(ft.icons.REMOVE, on_click=minus_click),
                txt_number,
                ft.IconButton(ft.icons.ADD, on_click=plus_click),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
    )

ft.app(main)