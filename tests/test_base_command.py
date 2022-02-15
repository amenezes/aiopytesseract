import pytest

import aiopytesseract


@pytest.mark.asyncio
@pytest.mark.parametrize("input_data", [[], {}, (), None])
async def test_execute_unsupported(input_data):
    with pytest.raises(NotImplementedError):
        await aiopytesseract.base_command.execute(
            input_data, "JPEG", 220, "eng", 3, 3, 3
        )


@pytest.mark.asyncio
async def test_build_cmd_args_with_user_patterns():
    command = await aiopytesseract.base_command._build_cmd_args(
        "stdout", 200, 3, 3, user_patterns="tests/samples/user_patterns.txt"
    )
    assert command == [
        "stdin",
        "stdout",
        "--dpi",
        "200",
        "--psm",
        "3",
        "--oem",
        "3",
        "--user-patterns",
        "tests/samples/user_patterns.txt",
        "stdout",
    ]
