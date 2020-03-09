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

business_talks = [
    'Кто должен общаться с бизнесом насчет фич продукта?',
    'Кто должен общаться с бизнесом насчет сроков запуска продукта?',
    'Кто должен общаться с бизнесом насчет стоимости эксплуатации продукта?',
]

arch_talks = [
    'Кто выбирает стэк технологий продукта? (язык разработки, архитектура, монолит/микросервисы, etc)',
    'Кто выбирает DB-стэк продукта? (всякие уровни кэширования и хранения пусть будут здесь же)',
    'Кто выбирает среду исполнения продукта? (железо: свое/арендованное, виртуалки, контейнеры; облака: одно или'\
        'несколько разных)',
    'Кто выбирает системы и источники мониторинга и логирования?',
    'А за безопасность кто отвечает?',
    'Делать новое все любят, а кто за gargabe collect отвечает? (удалить ненужные ветки в репо, грохнуть тестовые'\
        'базы)',
    'Garbage collecting провели, все старое удалили, а вот за backup и восстановление из бэкапа кто ответит?',
]

cto_name = "CTO/CIO/IT Менеджер"

def extra_stats(df):
    def count_me_in(column_name):
        result = Counter()
        for row in df.iterrows():
            d = row[1]
            if d[who_am_i] in str(d[column_name]).split(","):
                result[d[who_am_i]] += 1
        return result

    good_is_me = count_me_in(who_is_good)
    bad_is_me = count_me_in(who_is_bad)

    print("Good is me")
    print(good_is_me)

    print("Bad is me")
    print(bad_is_me)

def main():
    df = read_file()
    extra_stats(df)

if __name__ == "__main__":
    main()