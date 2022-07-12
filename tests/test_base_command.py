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
@pytest.mark.parametrize(
    "args, expected",
    [
        (
            [
                "stdout",
                200,
                3,
                1,
                None,
                "tests/samples/user_patterns.txt",
                "/tessdata-test",
            ],
            [
                "--tessdata-dir",
                "/tessdata-test",
                "--user-patterns",
                "tests/samples/user_patterns.txt",
                "stdin",
                "stdout",
                "--dpi",
                "200",
                "--psm",
                "3",
                "--oem",
                "1",
                "stdout",
            ],
        ),
        (
            ["stdout", 300, 3, 3],
            ["stdin", "stdout", "--dpi", "300", "--psm", "3", "--oem", "3", "stdout"],
        ),
        (
            ["stdout", 300, 3, 3, "tests/samples/user_words.txt"],
            [
                "--user-words",
                "tests/samples/user_words.txt",
                "stdin",
                "stdout",
                "--dpi",
                "300",
                "--psm",
                "3",
                "--oem",
                "3",
                "stdout",
            ],
        ),
        (
            ["stdout", 300, 3, 3, None, None, "tessdata"],
            [
                "--tessdata-dir",
                "tessdata",
                "stdin",
                "stdout",
                "--dpi",
                "300",
                "--psm",
                "3",
                "--oem",
                "3",
                "stdout",
            ],
        ),
        (
            ["stdout", 300, 3, 3, None, None, None, "por+lat"],
            [
                "stdin",
                "stdout",
                "--dpi",
                "300",
                "--psm",
                "3",
                "--oem",
                "3",
                "-l",
                "por+lat",
                "stdout",
            ],
        ),
    ],
)
async def test_build_cmd_args_with_user_patterns(args, expected):
    command = await aiopytesseract.base_command._build_cmd_args(*args)
    assert command == expected
