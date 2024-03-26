from enum import StrEnum

from emoji import emojize


class RedisKeys(StrEnum):
    USERS_LIST_KEY = 'users'
    USER_KEY = 'user'
    SCENARIO_KEY = 'scenario'
    WORK_TYPES_KEY = 'work_types'
    CLIENTS_KEY = 'clients'
    WORK_TIME_REPORT_KEY = 'work_time_report'
    WORK_TIME_REPORT_STAT_KEY = 'work_time_report_stat'
    WORK_TIME_REPORT_LOCK_KEY = 'work_time_report_lock'


class MenuButtons(StrEnum):
    TIME_REPORT = 'Отчет по рабочему времени'
    CLIENT_REPORT = 'Отчет по клиентам'

    @classmethod
    def list(cls):
        return [e.value for e in cls]


class Notifications:
    SAVE_IN_PROGRESS = emojize('Сохраняем данные :floppy_disk:')
    SAVING_PROBLEM = emojize('Произошла ошибка при сохранении данных :face_screaming_in_fear:')
    SAVING_SUCCESS = emojize('Данные успешно сохранены :check_mark:')
    CALLBACK_DATA_ERROR = emojize('Ошибка в полученном запросе :thinking_face:')
    RETRY_OR_CALL_ADMIN = emojize('Попробуйте еще раз или обратитесь к администратору')


class Replies:
    SKIP = 'Пропустить'

    WRONG_PERSONAL_CODE = emojize('Хмм... :thinking_face:  Не могу авторизовать по введенному коду')
    PLEASE_AUTH = 'Для работы с ботом необходимо авторизоваться'
    ENTER_PERSONAL_CODE = emojize('Введите ваш уникальный код :input_numbers:')
    CHOOSE_MENU = 'Выберите пункт меню'

    ENTER_DATE = 'Введите дату в формате ДД.ММ.ГГГГ'
    CHOOSE_DATE = emojize('Или выберите из календаря :spiral_calendar:')
    WRONG_DATE_FORMAT = emojize('Неверный формат даты :man_facepalming:')

    CHOOSE_WORK_TYPE = emojize('Выберите вид работы из списка :toolbox:')
    WRONG_WORK_TYPE = emojize('Не могу найти такой вид работы :man_shrugging:')
    CHOOSE_CLIENT = emojize('Выберите клиента из списка :open_file_folder:')
    WRONG_CLIENT = emojize('Не могу найти такого клиента :man_shrugging:')

    ENTER_TIME = 'Введите затраченное время в формате ЧЧ:ММ'
    CHOOSE_TIME = emojize('Или выберите из списка :alarm_clock:')
    WRONG_TIME_FORMAT = emojize('Неверный формат времени :man_facepalming:')

    ENTER_COMMENT = 'Добавьте комментарий'

    NO_REPORTS = emojize('Отчетов нет')
    BACK_TO_MENU = emojize('Вернуться в меню')

    LOADING = emojize('Идёт загрузка данных :man_walking:')
