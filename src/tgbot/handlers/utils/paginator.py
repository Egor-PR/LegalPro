from enum import StrEnum

from aiogram.filters.callback_data import CallbackData


class ReportPaginatorAct(StrEnum):
    NEXT_PAGE = 'next_page'
    PREV_PAGE = 'prev_page'
    IGNORE = 'ignore'
    REMOVE = 'remove'


class ReportPaginatorCallback(CallbackData, prefix='report_paginator'):
    report_id: int
    act: str
    page: int
    report_id: int | None = None
