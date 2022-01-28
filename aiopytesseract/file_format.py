from enum import Enum, unique


@unique
class FileFormat(str, Enum):
    TXT: str = "txt"
    PDF: str = "pdf"
    HOCR: str = "hocr"
    STDOUT: str = "stdout"

    def __str__(self) -> str:
        return str.__str__(self)
