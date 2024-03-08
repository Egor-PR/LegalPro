from enum import StrEnum

from emoji import emojize


class MenuButtons(StrEnum):
    TIME_REPORT = 'Отчет по рабочему времени'
    CLIENT_REPORT = 'Отчет по клиентам'


class Replies:
    PLEASE_AUTH = 'Для работы с ботом необходимо авторизоваться'
    ENTER_PERSONAL_CODE = emojize('Введите ваш уникальный код :input_numbers:')
    CHOOSE_MENU = 'Выберите пункт меню'
