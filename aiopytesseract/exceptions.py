class TesseractError(Exception):
    def __init__(self, message: str = "Tesseract Error") -> None:
        self.message = message
        super().__init__(self.message)


class PSMInvalidException(TesseractError):
    def __init__(self, psm_value: int) -> None:
        message = f"PSM value must be in the range [0-13], got: {psm_value}"
        super().__init__(message)


class OEMInvalidException(TesseractError):
    def __init__(self, oem_value: int) -> None:
        message = f"OEM value must be in the range [0-3], got: {oem_value}"
        super().__init__(message)


class NoSuchFileException(TesseractError):
    def __init__(self, file_path: str) -> None:
        message = f"No such file: '{file_path}'"
        super().__init__(message)


class LanguageInvalidException(TesseractError):
    def __init__(
        self, language: str, available_languages: list[str] | None = None
    ) -> None:
        if available_languages:
            message = f"Language '{language}' is invalid. Available: {', '.join(available_languages[:5])}{'...' if len(available_languages) > 5 else ''}"
        else:
            message = f"Language '{language}' is invalid"
        super().__init__(message)


class TesseractRuntimeError(TesseractError):
    def __init__(self, stderr_output: str = "") -> None:
        message = (
            f"Tesseract process failed: {stderr_output}"
            if stderr_output
            else "Tesseract process failed"
        )
        super().__init__(message)


class TesseractTimeoutError(TesseractError):
    def __init__(self, timeout: float | None = None) -> None:
        message = (
            f"Tesseract process timeout after {timeout}s"
            if timeout
            else "Tesseract process timeout"
        )
        super().__init__(message)


class TesseractNotFoundError(TesseractError):
    def __init__(self) -> None:
        message = "Tesseract binary not found. Please install tesseract-ocr"
        super().__init__(message)


class ImageFormatError(TesseractError):
    def __init__(self, image_type: type) -> None:
        message = f"Image type '{image_type.__name__}' is not supported. Use str (file path) or bytes"
        super().__init__(message)
