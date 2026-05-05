from datetime import datetime
from zoneinfo import ZoneInfo
import json
import calendar
from re import fullmatch
import os

TODAY = datetime.now().astimezone()         # местное время и дата сейчас

def time_to_utc(dt):
    return dt.astimezone(ZoneInfo('UTC'))   # перевод даты/времени в UTC

def time_from_utc(dt):
    my_tz = TODAY.tzinfo                    # местный часовой пояс
    return dt.astimezone(tz=my_tz)          # перевод даты/времени из UTC в местный формат


def is_correct_date(str_dt, flag=True):
    r = [r'\b0*(?:[1-9]|[1-2]\d|[3][01])\b',
         r'\b0*(?:[1-9]|1[0-2])\b',
         r'\b\d+\b',
         r'\b0*(?:\d|1\d|2[0-3])\b',
         r'\b0*(?:\d|[1-5]\d)\b']
    if flag:
        regex = rf"({r[0]})[\.\s/]+({r[1]})[\.\s/]+({r[2]})[\.\s]+({r[3]})[\.:\s]+({r[4]})"
    else:
        regex = rf"({r[0]})[\.\s/]+({r[1]})[\.\s/]+({r[2]}).*"
    return fullmatch(regex, str_dt.strip())



def start_greeting():
    '''Стартовое приветствие'''
    print('------- Календарь-планировщик ™ -------')
    print(TODAY.strftime('Сегодня: %d.%m.%Y (%A)\nМестное время: %H:%M\n'))
    show_month(today=True)



def show_month(today=False):
    '''Показывает календарь на указанный период, дни в которые есть события, отмечены *'''
    if today:
        input_date = f'{TODAY.month} {TODAY.year}'.split()
    else:
        input_date = input('Введите месяц и год: ').split()
    if len(input_date) == 2 and input_date[0].isdigit() and input_date[1].isdigit():
        m, y  = map(int, input_date)
        cal = calendar.Calendar()
        dates_iter = cal.itermonthdates(y, m)
        print(tuple(calendar.month_name)[m], y)
        print(calendar.weekheader(4))  # названия дней недели

        line = []
        for day in dates_iter:
            if day.month == m and day in events.keys():
                line.append(f'*{day.day: >2}')
            elif day.month == m:
                line.append(f"{day.day: >3}")
            else:
                line.append('   ')
            if day.weekday() == calendar.SUNDAY:
                print('  '.join(line))
                line = []
    else:
        print('Ошибка! Неверно введены исходные данные, правильный формат: show YYYY MM')
    print('---------------------------------------')



def json_to_file(data):
    '''Сохранение словаря событий в json-файл + серилизация дат в словаре в формат iso'''
    data_iso = {}
    for day, events_list in data.items():
        new_events_list = []
        for event in events_list:
            new_event = {'event_time_utc': event['event_time_utc'].isoformat(), 'description': event['description']}
            new_events_list.append(new_event)
        data_iso[day.isoformat()] = new_events_list

    with open("events.json", "w", encoding="utf-8") as json_file:
        json.dump(data_iso, json_file, indent=4, ensure_ascii=False)



def file_to_dict():
    '''Чтение словаря событий из json-файла в словарь + серилизация дат в словаре из iso-формата в utc'''
    if not os.path.exists("events.json") or not os.path.isfile('events.json'):
        print('Нет записанных событий')
        return {}

    with open("events.json", "r", encoding="utf-8") as json_file:
        data = json.load(json_file)
    data_utc = {}
    for day, events_list in data.items():
        new_events_list = []
        for event in events_list:
            new_event = {'event_time_utc': datetime.fromisoformat(event['event_time_utc']), 'description': event['description']}
            new_events_list.append(new_event)
        data_utc[datetime.fromisoformat(day).date()] = new_events_list
    return data_utc




def add_event(event_dict):
    '''Добавление нового события в календарь'''
    print('Добавление нового события в календарь.')
    input_date = input('Введите дату и время события <ДД.ММ.ГГГГ ЧЧ:ММ> : ')
    event_date = is_correct_date(input_date, flag=True)
    if event_date:
        d, mo, y, h, mi =  map(int, event_date.groups())
        dt = datetime(y,mo,d,h,mi).astimezone()
        event= input('Введите описание события: ')
        key = dt.date()
        dct = {'event_time_utc' : dt.astimezone(ZoneInfo('UTC')),
               'description' : event}
        event_dict.setdefault(key, [])
        event_dict[dt.date()].append(dct)
        json_to_file(event_dict)
        print(f"Событие добавлено в календарь: \n"
              f"{dt.strftime('[%d.%m.%Y  %H:%M]')}   Описание: {event}")
    else:
        print('Неверная дата или время!')
    print('-' * 50)
    return event_dict


def view_events(event_dict):
    '''Отображение событий за указанный день'''
    input_date = input('Введите дату <ДД.ММ.ГГГГ>: ')
    dt_match = is_correct_date(input_date, flag=False)
    if not dt_match:
        print('Неверный ввод даты!')
    else:
        d = datetime(*map(int, dt_match.groups()[::-1])).date()
        lst = event_dict.get(d)
        if not lst:
            print(f"В календаре нет сохранённых событий на дату {d.strftime('%d.%m.%Y')}г.")
        else:
            print(f"В календаре на {d.strftime('%d.%m.%Y')}г. найдены события:")
            for dct in sorted(lst, key=lambda x : x['event_time_utc']):
                print(f"{time_from_utc(dct['event_time_utc']).strftime('%H:%M')} - {dct['description']}")
    print('---------------------------------------')


# ----------------- основной код -----------------------
# Считываю словарь для записи событий
events = file_to_dict()
start_greeting()

while True:
    task = input('Введите команду (show, add, view, exit): ').strip().split()
    match task[0]:
        case 'show': show_month()
        case 'add' : events = add_event(events)
        case 'view': view_events(events)
        case 'exit':
            print('Работа программы завершена')
            break
        case _ :
            print('Неизвестная команда, введите одну из команд: show, add, view, exit.')



