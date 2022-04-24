from aiopytesseract.exceptions import TesseractError


def test_exception_to_str():
    message = str(TesseractError("test"))
    assert isinstance(message, str)
