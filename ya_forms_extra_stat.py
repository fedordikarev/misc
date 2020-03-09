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

cto_name = "CTO/CIO/IT Менеджер"
sys_name = "Системный администратор"
dev_name = "Разработчик"
arch_talks = [
    {"q":'Кто выбирает стэк технологий продукта? (язык разработки, архитектура, монолит/микросервисы, etc)',
     "extra": [cto_name, dev_name]},
    {"q":'Кто выбирает DB-стэк продукта? (всякие уровни кэширования и хранения пусть будут здесь же)',
     "extra": [cto_name, "DBA"]},
    {"q":'Кто выбирает среду исполнения продукта? (железо: свое/арендованное, виртуалки, контейнеры; облака: одно или '\
        'несколько разных)',
     "extra": [cto_name, sys_name]},
    {"q":'Кто выбирает системы и источники мониторинга и логирования?',
     "extra": [sys_name]},
    {"q":'А за безопасность кто отвечает?',
     "extra": [sys_name]},
    {"q":'Делать новое все любят, а кто за gargabe collect отвечает? (удалить ненужные ветки в репо, грохнуть тестовые '\
        'базы)',
     "extra": [dev_name, "DevOps"]},
    {"q":'Garbage collecting провели, все старое удалили, а вот за backup и восстановление из бэкапа кто ответит?',
     "extra": [sys_name]},
]


def extra_stats(df):
    def count_me_in(column_name, extra_persons=[]):
        result = Counter()
        result_extra = Counter()
        for row in df.iterrows():
            d = row[1]
            if d[who_am_i] in str(d[column_name]).split(", "):
                result[d[who_am_i]] += 1
                # print(">>>", extra_persons)
                for person in extra_persons:
                    if person == d[who_am_i]:
                        continue
                    if person in str(d[column_name]).split(", "):
                        result_extra[(d[who_am_i], person)] += 1
                        # print(d[who_am_i], d[column_name])
                        # print(result_extra)
        return result, result_extra

    good_is_me, _ = count_me_in(who_is_good)
    bad_is_me, _ = count_me_in(who_is_bad)

    print("Good is me")
    print(good_is_me)

    print("Bad is me")
    print(bad_is_me)

    print("=== Разговоры с бизнесом ===")
    for talk in business_talks:
        result_me, result_me_with_cto = count_me_in(talk, [cto_name])
        print(talk)
        print("Me ", result_me)
        print("Me and {} ".format(cto_name), result_me_with_cto)
        print()
    print("=== Разговоры за Архитектуру ===")
    for talk in arch_talks:
        result_me, result_me_with_extra = count_me_in(talk["q"], talk.get("extra", []))
        print(talk["q"])
        print("Me ", result_me)
        if result_me_with_extra:
            print("Me and Extra", result_me_with_extra)
        print()

def main():
    df = read_file()
    extra_stats(df)

if __name__ == "__main__":
    main()
