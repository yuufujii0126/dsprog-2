import pandas as pd

orders = pd.read_csv('/Users/fujiiyuu/dsprog-2/課題用/orders.csv')
items = pd.read_csv('/Users/fujiiyuu/dsprog-2/課題用/items.csv')
users = pd.read_csv('/Users/fujiiyuu/dsprog-2/課題用/users.csv')

merged_o_i_df = pd.merge(orders, items, on='item_id')
merged_df = pd.merge(merged_o_i_df, users, on='user_id')

merged_df['order_amount'] = merged_df['order_num'] * merged_df['item_price']
merged_df['user_amount_avg'] = merged_df.groupby('user_id')['order_amount'].transform('mean')

result = merged_df[['user_id', 'user_name', 'user_amount_avg']].drop_duplicates()

max_user_amount_avg = result['user_amount_avg'].max()
max_user = result.loc[result['user_amount_avg'] == max_user_amount_avg]

print(f"[{max_user['user_id'].values[0]}, {max_user['user_amount_avg'].values[0]}]")