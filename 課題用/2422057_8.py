import pandas as pd

df = pd.read_csv('/Users/fujiiyuu/dsprog-2/課題用/winequality-red.csv')
df.query('quality >= 6').sort_values('quality', ascending
=False)
print(df.query('quality >= 6').sort_values('quality', ascending=False))