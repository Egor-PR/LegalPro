from dataclasses import dataclass, asdict


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

    def get_list(self) -> list[str]:
        return [
            self.report_date,
            self.user_id,
            self.user_fullname,
            self.user_job_title,
            self.work_type,
            self.client,
            self.hours,
            self.comment,
        ]
