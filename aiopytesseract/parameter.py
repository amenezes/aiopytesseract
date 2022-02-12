from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Parameter:
    name: str
    value: str
    description: str
