import functools
from typing import Any

import click

COLORS = ("red", "green", "yellow", "blue", "black", "magenta", "cyan", "white")

COLORS += tuple(f"bright_{color}" for color in COLORS)


class _IO:
    NORMAL = 0
    DETAIL = 1
    DEBUG = 2

    def __init__(self, verbosity: int = NORMAL, disable_colors: bool = False) -> None:
        self.verbosity = verbosity
        self.disable_colors = disable_colors

        for color in COLORS:
            setattr(self, color, functools.partial(self._style, fg=color))

    def disable(self) -> None:
        self.disable_colors = False

    def set_verbosity(self, verbosity: int) -> None:
        self.verbosity = verbosity

    def echo(
        self, message: Any = None, err: bool = False, verbosity: int = NORMAL
    ) -> None:
        if self.verbosity >= verbosity:
            click.echo(message, err=err)

    def _style(self, text: str, *args, **kwargs) -> str:
        if self.disable_colors:
            return text
        else:
            return click.style(text, *args, **kwargs)
