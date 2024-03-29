from dataclasses import dataclass, asdict


@dataclass
class WorkType:
    name: str

    dict = asdict
