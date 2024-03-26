import re
from dataclasses import dataclass, asdict


@dataclass
class WorkTimeReportStat:
    report_date: str
    time_plan: str | None = None
    time_fact: str | None = None
    time_net: str | None = None

    dict = asdict

    def get_msg(self):
        report_date = re.escape(self.report_date)
        time_plan = re.escape(self.time_plan if self.time_plan else '0')
        time_fact = re.escape(self.time_fact if self.time_fact else '0')
        time_net = re.escape(self.time_net if self.time_net else '0')
        return f"""
*Общий отчет {report_date}*

План: *{time_plan} ч*
Факт: *{time_fact} ч*
Сальдо: *{time_net} ч*
"""


@dataclass
class WorkTimeReport:
    report_date: str
    user_id: str
    user_fullname: str
    work_type: str
    client: str
    hours: str
    comment: str | None = None
    user_job_title: str | None = None
    row_id: int | None = None

    dict = asdict

    def get_list(self) -> list[str]:
        return [
            self.report_date,
            self.user_id,
            self.user_fullname,
            self.user_job_title if self.user_job_title else '-',
            self.work_type,
            self.client,
            self.hours,
            self.comment if self.comment else '-',
        ]

    def get_msg(self):
        return f"""
Вид работы: *{self.work_type}*
Клиент: *{self.client}*
Часы: *{self.hours}*        
"""
