import pytest

from aiopytesseract import constants, exceptions, validators


@pytest.mark.asyncio
async def test_valid_psm():
    for psm in constants.PAGE_SEGMENTATION_MODES.keys():
        await validators.psm_is_valid(psm)


@pytest.mark.asyncio
@pytest.mark.parametrize("psm", [-1, 14, "1"])
async def test_invalid_psm(psm):
    with pytest.raises(exceptions.PSMInvalidException):
        await validators.psm_is_valid(psm)


@pytest.mark.asyncio
async def test_valid_oem():
    for oem in constants.OCR_ENGINE_MODES.keys():
        await validators.oem_is_valid(oem)


@pytest.mark.asyncio
@pytest.mark.parametrize("oem", [-1, 4, "1"])
async def test_invalid_oem(oem):
    with pytest.raises(exceptions.OEMInvalidException):
        await validators.oem_is_valid(oem)


@pytest.mark.asyncio
async def test_file_exists():
    await validators.file_exists("tests/samples/file-sample_150kB.png")


@pytest.mark.asyncio
async def test_file_does_not_exist():
    with pytest.raises(exceptions.NoSuchFileException):
        await validators.file_exists("tests/samples/file-sample_150kB.jpeg")
