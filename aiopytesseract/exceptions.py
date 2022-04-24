class TesseractError(Exception):
    """Base exception for tesseract"""

    def __init__(self, message: str = ""):
        self.message = message
    
    def __str__(self):
        return self.message


class PSMInvalidException(TesseractError):    
    def __init__(self, message="PSM Invalid"):
        super().__init__(message)


class OEMInvalidException(TesseractError):
    def __init__(self, message="OEM Invalid"):
        super().__init__(message)


class NoSuchFileException(TesseractError):
    def __init__(self, message="No such file"):
        super().__init__(message)


class LanguageInvalidException(TesseractError):
    def __init__(self, message="Language invalid"):
        super().__init__(message)


class TesseractRuntimeError(TesseractError):
    pass


class TesseractTimeoutError(TesseractRuntimeError):
    def __init__(self, message="Tesseract process timeout"):
        super().__init__(message)
