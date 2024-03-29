from dataclasses import dataclass, asdict


@dataclass
class ScenarioStep:
    number: int
    result: str | None = None

    dict = asdict


@dataclass
class Scenario:
    name: str
    steps: list[ScenarioStep]
    current_step: int = 1

    dict = asdict
