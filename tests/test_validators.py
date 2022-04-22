import pytest

from aiopytesseract import constants, exceptions, validators


async def test_valid_psm():
    for psm in constants.PAGE_SEGMENTATION_MODES.keys():
        validators.psm_is_valid(psm)


@pytest.mark.parametrize("psm", [-1, 14, "1"])
def test_invalid_psm(psm):
    with pytest.raises(exceptions.PSMInvalidException):
        validators.psm_is_valid(psm)


def test_valid_oem():
    for oem in constants.OCR_ENGINE_MODES.keys():
        validators.oem_is_valid(oem)


@pytest.mark.parametrize("oem", [-1, 4, "1"])
def test_invalid_oem(oem):
    with pytest.raises(exceptions.OEMInvalidException):
        validators.oem_is_valid(oem)


async def test_file_exists():
    validators.file_exists("tests/samples/file-sample_150kB.png")


def test_file_does_not_exist():
    with pytest.raises(exceptions.NoSuchFileException):
        validators.file_exists("tests/samples/file-sample_150kB.jpeg")


@pytest.mark.parametrize("lang", ["por", "por+eng", "por+eng+fra"])
async def test_language_is_valid(lang):
    resp = validators.language_is_valid(lang)
    assert resp is None


@pytest.mark.parametrize("lang", ["por eng", "por:eng", "por-eng", "por+zuul"])
async def test_language_is_invalid(lang):
    with pytest.raises(exceptions.LanguageInvalidException):
        validators.language_is_valid(lang)
