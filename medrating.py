#!/usr/bin/env python3

"""
Есть API для получения списка задач и api для получения списка юзеров:
https://json.medrating.org/todos
https://json.medrating.org/users
Используя только эти API составить отчёты по всем юзерам в отдельных текстовых файлах.
После запуска скрипта, рядом должна появиться директория "tasks" с текстовыми файлами. Файл называть по username пользователя в формате "Antonette.txt"
Внутри файла на первой строке писать полное имя, и рядом в < > записывать email. Через пробел от email записывать время составления отчёта в формате 23.09.2020 15:25
На второй строке записывать название компании, в которой работает юзер.
Третья строка должна быть пустой.
На четвёртой строке "Завершённые задачи:" и далее список названий завершённых задач.
После завершённых задач через пустую строку записать "Оставшиеся задачи:" и вывести остальные задачи.
Если название задачи больше 50 символов, то обрезать до 50 символов и добавить троеточие.
Пример файла:
```
Ervin Howell <Shanna@melissa.tv> 23.09.2020 15:25
Deckow-Crist
Завершённые задачи:
distinctio vitae autem nihil ut molestias quo
Оставшиеся задачи:
suscipit repellat esse quibusdam voluptatem incidu...
laborum aut in quam
```
Если файл для пользователя уже существует, то существующий файл переименовать, добавив в него время составления этого старого отчёта в формате "Antonette_2020-09-23T15:25.txt"
Таким образом, актуальный отчёт всегда будет без даты в названии. Старые отчёты не удаляются, а переименовываются.
Код должен быть чистым, без необоснованных повторений, с выделенем функций, где это уместно, с говорящими именами.
Код сделать максимально эффективным, но не в ущерб читабельности. Подсказка: следует избегать частых записей на диск.
Предусмотреть возможные сбои в сети или при записи на диск. Не должно быть наполовину сформированных файлов. Либо файл есть и он целиком корректный, либо его нет.
Если по юзеру однажды был создан отчёт, то всегда должен существовать актуальный отчёт без даты в названии. Не должно быть такого, что из-за сбоя в сети или т.п. остались только файлы с датами в названиях.
Если какие-то моменты не обговорены в задаче, то продумайте плюсы и минусы возможных вариантов, и выберите наиболее подходящий на ваш взгляд, чтобы потом можно было обосновать своё решение.
Предусмотреть крайние случаи (у пользователя нет задач, и т.п.).
Код должен быть оформлен по pep8.
Использовать местное время.
Программа должна корректно работать на linux (Debian, Ubuntu).
Можно использовать любые библиотеки.
"""

import requests
import json
import os
import datetime as dt
from collections import defaultdict

api_base = "https://json.medrating.org"
api_user = "{}/users".format(api_base)
api_todos = "{}/todos".format(api_base)
max_task_name_len = 50
out_dir = "tasks"

def read_data():
    users = requests.get(api_user).json()
    todos = requests.get(api_todos).json()
    return users, todos

def prepare_report(todos):
    completed = defaultdict(list)
    uncompleted = defaultdict(list)
    for task in todos:
        if task['completed']:
            completed[task['userId']].append(task['title'])
        else:
            uncompleted[task['userId']].append(task['title'])

    return completed, uncompleted

def format_report(user, completed, uncompleted):
    def task_name(name):
        ### TODO: check name uniqness, add task id to title and so
        return name if len(name) <= max_task_name_len else name[:max_task_name_len]+'...'

    now_time = dt.datetime.now().strftime("%d.%m.%Y %H:%M")
    yield "{name} <{email}> {date}".format(name=user['name'], email=user['email'], date=now_time)
    yield user['company']['name']
    yield ''
    yield 'Завершенные задачи:'
    for task in completed:
        yield task_name(task)
    yield ''
    yield 'Оставшиеся задачи:'
    for task in uncompleted:
        yield task_name(task)


def main():
    users, todos = read_data()
    completed, uncompleted = prepare_report(todos)

    print("\n".join(format_report(users[0], completed[users[0]['id']], uncompleted[users[0]['id']])))

if __name__ == "__main__":
    main()
