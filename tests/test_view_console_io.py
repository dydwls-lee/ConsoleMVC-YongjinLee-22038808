from view.console_io import ConsoleIO


def test_show_prints_given_text():
    printed = []
    io = ConsoleIO(print_func=printed.append, input_func=lambda _: "")

    io.show("hello")

    assert printed == ["hello"]


def test_prompt_returns_stripped_input():
    io = ConsoleIO(print_func=lambda *_: None, input_func=lambda prompt: "  S-001  ")

    result = io.prompt("시료 ID: ")

    assert result == "S-001"


def test_show_error_prefixes_message():
    printed = []
    io = ConsoleIO(print_func=printed.append, input_func=lambda _: "")

    io.show_error("문제 발생")

    assert printed == ["[오류] 문제 발생"]
