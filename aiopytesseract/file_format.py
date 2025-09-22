from enum import StrEnum, unique


@unique
class FileFormat(StrEnum):
    ALTO = "alto"
    HOCR = "hocr"
    PDF = "pdf"
    TSV = "tsv"
    TXT = "txt"
    OSD = "osd"
