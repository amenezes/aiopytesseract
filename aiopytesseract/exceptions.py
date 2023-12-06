class TesseractError(Exception):
    """Base exception for tesseract"""

    def __init__(self, message: str = "Tesseract Error") -> None:
        self.message = message

    def __str__(self) -> str:
        return self.message


class PSMInvalidException(TesseractError):
    def __init__(
        self, message: str = "PSM value must be in the range [0 - 13]"
    ) -> None:
        super().__init__(message)


class OEMInvalidException(TesseractError):
    def __init__(self, message: str = "OEM value must be in the range [0 - 3]") -> None:
        super().__init__(message)


class NoSuchFileException(TesseractError):
    def __init__(self, message: str = "No such file") -> None:
        super().__init__(message)


class LanguageInvalidException(TesseractError):
    def __init__(self, message: str = "Language invalid") -> None:
        super().__init__(message)


class TesseractRuntimeError(TesseractError):
    pass


class TesseractTimeoutError(TesseractRuntimeError):
    def __init__(self, message: str = "Tesseract process timeout") -> None:
        super().__init__(message)
