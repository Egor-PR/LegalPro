from dataclasses import dataclass


@dataclass
class User:
    fullname: str
    id: str
    admin: bool = False
    job_title: str | None = None
    is_active: bool = False
    chat_id: int | None = None
