import pandas as pd

orders = pd.read_csv('/Users/fujiiyuu/dsprog-2/課題用/orders.csv')
items = pd.read_csv('/Users/fujiiyuu/dsprog-2/課題用/items.csv')
users = pd.read_csv('/Users/fujiiyuu/dsprog-2/課題用/users.csv')


# 各注文における購入金額を算出
df = pd.merge(orders, items, on='item_id')  # itemsテーブルを結合
df = pd.merge(df, users, on='user_id')  # usersテーブルを結合
df['total'] = df['item_price'] * df['order_num']  # 購入金額を算出

# 最も高い購入金額とそのorder_idを取得
max_total = df['total'].max()
max_order_id = df[df['total'] == max_total]['order_id'].values[0]
print(max_order_id, max_total)