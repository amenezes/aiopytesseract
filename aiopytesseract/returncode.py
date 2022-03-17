from enum import IntEnum, unique


@unique
class ReturnCode(IntEnum):
    SUCCESS = 0
    FAILED = 1
