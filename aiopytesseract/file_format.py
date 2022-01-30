from enum import Enum, unique


@unique
class FileFormat(str, Enum):
    ALTO: str = "alto"
    HOCR: str = "hocr"
    PDF: str = "pdf"
    TSV: str = "tsv"
    TXT: str = "txt"
    STDOUT: str = "stdout"
    STDIN: str = "stdin"

    def __str__(self) -> str:
        return str.__str__(self)
