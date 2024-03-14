from enum import StrEnum

from emoji import emojize


class RedisKeys(StrEnum):
    USERS_LIST_KEY = 'users'
    USER_KEY = 'user'
    SCENARIO_KEY = 'scenario'
    WORK_TYPES_KEY = 'work_types'
    CLIENTS_KEY = 'clients'


class MenuButtons(StrEnum):
    TIME_REPORT = 'Отчет по рабочему времени'
    CLIENT_REPORT = 'Отчет по клиентам'

    @classmethod
    def list(cls):
        return [e.value for e in cls]


class Replies:
    WRONG_PERSONAL_CODE = emojize('Хмм... :thinking_face:  Не могу авторизовать по введенному коду')
    PLEASE_AUTH = 'Для работы с ботом необходимо авторизоваться'
    ENTER_PERSONAL_CODE = emojize('Введите ваш уникальный код :input_numbers:')
    CHOOSE_MENU = 'Выберите пункт меню'

    ENTER_DATE = 'Введите дату в формате ДД.ММ.ГГГГ'
    CHOOSE_DATE = emojize('Или выберите из календаря :spiral_calendar:')
    WRONG_DATE_FORMAT = emojize('Неверный формат даты :man_facepalming:')
