import pandas as pd

orders = pd.read_csv('/Users/fujiiyuu/dsprog-2/課題用/orders.csv')
items = pd.read_csv('/Users/fujiiyuu/dsprog-2/課題用/items.csv')
users = pd.read_csv('/Users/fujiiyuu/dsprog-2/課題用/users.csv')

import pandas as pd

def recommend_items(data, target_id, top_n=3):
    # 基準商品を取得
    target_item = data[data["item_id"] == target_id].iloc[0]

    # 同じ商品を除外
    candidates = data[data["item_id"] != target_id].copy()

    # 類似性をスコア化する列を追加
    candidates["score"] = 0

    # ルール1: 小カテゴリ → 大カテゴリ
    candidates.loc[candidates["small_category"] == target_item["small_category"], "score"] += 100
    candidates.loc[candidates["big_category"] == target_item["big_category"], "score"] += 10

    # ルール2: 価格が近いものを優先
    candidates["price_diff"] = abs(candidates["item_price"] - target_item["item_price"])

    # ルール3: ページ数が近いものを優先
    candidates["pages_diff"] = abs(candidates["pages"] - target_item["pages"])

    # スコア順、価格差順、ページ数差順でソート
    sorted_candidates = candidates.sort_values(
        by=["score", "price_diff", "pages_diff"], ascending=[False, True, True]
    )

    # 上位N件を取得
    return sorted_candidates[["item_id", "item_name", "item_price", "big_category", "small_category", "pages"]].head(top_n)

# CSVファイルを読み込む
file_path = "items.csv"  # 実際のファイルパスを指定してください
items_data = pd.read_csv(file_path)

# 推薦商品の取得
target_id = 101  # 推薦の基準となる商品ID
recommended_items = recommend_items(items_data, target_id)

# 推薦結果のitems_idのみを表示
print("推薦商品の上位3件:")
print(recommended_items["item_id"].values)


