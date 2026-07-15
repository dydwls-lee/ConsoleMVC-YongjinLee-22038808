"""Thin console I/O wrapper.

Wraps print()/input() so the Controller layer never touches the
console directly and so tests can inject fakes instead of the real
built-ins. Holds no business logic.
"""

from __future__ import annotations

from typing import Callable


class ConsoleIO:
    def __init__(
        self,
        print_func: Callable[[str], None] = print,
        input_func: Callable[[str], str] = input,
    ) -> None:
        self._print = print_func
        self._input = input_func

    def show(self, text: str) -> None:
        self._print(text)

    def show_error(self, text: str) -> None:
        self._print(f"[오류] {text}")

    def prompt(self, message: str) -> str:
        return self._input(message).strip()
