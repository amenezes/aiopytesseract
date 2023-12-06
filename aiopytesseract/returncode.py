from enum import IntEnum, unique


@unique
class ReturnCode(IntEnum):
    SUCCESS: int = 0
    FAILED: int = 1
