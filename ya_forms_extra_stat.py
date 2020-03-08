import pandas as pd
from collections import Counter
import os

def read_file(fname=None):
    if fname is None:
        fname = os.path.expanduser("~/Downloads/answers.zip")

    return pd.read_csv(fname)

who_am_i = 'Ваш основной функционал на работе'
who_is_good = 'Ну и напоследок: кто самый лапочка в компании и самый молодец?'
who_is_bad = 'И совсем напоследок: а из-за кого больше всего проблем и кто самый бяка?'

def extra_stats(df):
    good_is_me = Counter()
    bad_is_me = Counter()
    for row in df.iterrows():
        d = row[1]
        if d[who_am_i] in str(d[who_is_good]).split(","):
            good_is_me[d[who_am_i]] += 1
            # print(d[who_am_i])
        if d[who_am_i] in str(d[who_is_bad]).split(","):
            bad_is_me[d[who_am_i]] += 1
    print("Good is me")
    print(good_is_me)

    print("Bad is me")
    print(bad_is_me)

def main():
    df = read_file()
    extra_stats(df)

if __name__ == "__main__":
    main()
