import pandas as pd
import sys

df = pd.read_csv('../data/final_df.csv')


def get_closing_probability(address):
    return df[(df['address']==address)]['closing_probability'].values[0]


if __name__ == "__main__":
    address = '735 S Green Valley Pkwy'
    prob = get_closing_probability(df, address)
    print(prob)
