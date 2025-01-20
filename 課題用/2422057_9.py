import pandas as pd

df = pd.read_csv('/Users/fujiiyuu/dsprog-2/課題用/winequality-red.csv')
print(df.groupby('quality').mean())