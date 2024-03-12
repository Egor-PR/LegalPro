import calendar
import logging
from datetime import datetime, timedelta

from aiogram.filters.callback_data import CallbackData
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

logger = logging.getLogger(__name__)


class CalendarCallback(CallbackData, prefix='simple_calendar'):
    act: str
    year: int
    month: int
    day: int


class SimpleCalendar:

    async def start_calendar(
        self,
        year: int = datetime.now().year,
        month: int = datetime.now().month,
        skip_calendar: bool = False,
    ) -> InlineKeyboardMarkup:
        """
        Creates an inline keyboard with the provided year and month
        :param skip_calendar: to skip calendar
        :param int year: Year to use in the calendar, if None the current year is used.
        :param int month: Month to use in the calendar, if None the current month is used.
        :return: Returns InlineKeyboardMarkup object with the calendar.
        """
        ignore_callback = CalendarCallback(act="IGNORE", year=year, month=month, day=0).pack()  # for buttons with no answer
        # First row - Month and Year
        months = {
            1: 'Январь',
            2: 'Февраль',
            3: 'Март',
            4: 'Апрель',
            5: 'Май',
            6: 'Июнь',
            7: 'Июль',
            8: 'Август',
            9: 'Сентябрь',
            10: 'Октябрь',
            11: 'Ноябрь',
            12: 'Декабрь',
        }
        zero_row = [
            InlineKeyboardButton(
                text=f'{months.get(month)} {str(year)}',
                callback_data=ignore_callback,
            ),
        ]
        first_row = [
            InlineKeyboardButton(
                text="<<",
                callback_data=CalendarCallback(act="PREV-YEAR", year=year, month=month,
                                               day=1).pack(),
            ),
            InlineKeyboardButton(
                text="<",
                callback_data=CalendarCallback(act="PREV-MONTH", year=year, month=month,
                                               day=1).pack(),
            ),
            InlineKeyboardButton(
                text=">",
                callback_data=CalendarCallback(act="NEXT-MONTH", year=year, month=month,
                                               day=1).pack(),
            ),
            InlineKeyboardButton(
                text=">>",
                callback_data=CalendarCallback(act="NEXT-YEAR", year=year, month=month,
                                               day=1).pack(),
            )
        ]
        # Second row - Week Days
        second_row = [
            InlineKeyboardButton(text=day, callback_data=ignore_callback)
            for day in ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        ]

        # Calendar rows - Days of month
        month_calendar = calendar.monthcalendar(year, month)
        calendar_rows = [
            [
                InlineKeyboardButton(text=" ", callback_data=ignore_callback) if day == 0
                else InlineKeyboardButton(
                    text=str(day),
                    callback_data=CalendarCallback(act="DAY", year=year, month=month, day=day).pack(),
                )
                for day in week
            ]
            for week in month_calendar
        ]

        inline_kb = InlineKeyboardMarkup(inline_keyboard=[
            first_row,
            zero_row,
            second_row,
            *calendar_rows,
        ])

        if skip_calendar:
            inline_kb.inline_keyboard.append([
                InlineKeyboardButton(
                    text="Пропустить",
                    callback_data=CalendarCallback(act="SKIP", year=year, month=month,
                                                   day=1).pack(),
                )
            ])

        builder = InlineKeyboardBuilder()
        builder.attach(InlineKeyboardBuilder.from_markup(inline_kb))
        return builder.as_markup()

    async def process_selection(self, query: CallbackQuery, data: CalendarCallback) -> tuple:
        """
        Process the callback_query. This method generates a new calendar if forward or
        backward is pressed. This method should be called inside a CallbackQueryHandler.
        :param query: callback_query, as provided by the CallbackQueryHandler
        :param data: callback_data, dictionary, set by calendar_callback
        :return: Returns a tuple (Boolean,datetime), indicating if a date is selected
                    and returning the date if so.
        """
        return_data = (False, None)
        temp_date = datetime(int(data.year), int(data.month), 1)
        # processing empty buttons, answering with no action
        if data.act == "IGNORE":
            await query.answer(cache_time=60)
        # user picked a day button, return date
        if data.act == "DAY":
            await query.message.delete_reply_markup()   # removing inline keyboard
            return_data = True, datetime(int(data.year), int(data.month), int(data.day))
        # user navigates to previous year, editing message with new calendar
        if data.act == "PREV-YEAR":
            prev_date = temp_date - timedelta(days=365)
            await query.message.edit_reply_markup(reply_markup=await self.start_calendar(int(prev_date.year), int(prev_date.month)))
        # user navigates to next year, editing message with new calendar
        if data.act == "NEXT-YEAR":
            next_date = temp_date + timedelta(days=365)
            await query.message.edit_reply_markup(reply_markup=await self.start_calendar(int(next_date.year), int(next_date.month)))
        # user navigates to previous month, editing message with new calendar
        if data.act == "PREV-MONTH":
            prev_date = temp_date - timedelta(days=1)
            await query.message.edit_reply_markup(inline_message_id=None, reply_markup=await self.start_calendar(int(prev_date.year), int(prev_date.month)))
        # user navigates to next month, editing message with new calendar
        if data.act == "NEXT-MONTH":
            next_date = temp_date + timedelta(days=31)
            await query.message.edit_reply_markup(reply_markup=await self.start_calendar(int(next_date.year), int(next_date.month)))
        if data.act == "SKIP":
            await query.message.delete_reply_markup()
            return_data = True, 'Пропустить'
        # at some point user clicks DAY button, returning date
        return return_data
