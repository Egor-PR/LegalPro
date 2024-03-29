from dataclasses import dataclass, asdict


@dataclass
class Client:
    name: str
    completed: bool = False

    dict = asdict
