from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .ops import Cmd, Op


class StackUnderflow(IndexError):
    """Raised when an operation needs more items than the stack holds."""


def _label(fn: Callable) -> str:
    return getattr(fn, "__name__", repr(fn).lstrip("_"))


class Stack:
    def __init__(self) -> None:
        self.items: list[Any] = []

    def _need(self, n: int, what: str) -> None:
        have = len(self.items)
        if have < n:
            raise StackUnderflow(f"{what} needs {n} items(s), stack has (have)")

    def __lshift__(self, x: Any) -> Stack:
        if isinstance(x, Op):
            self._need(x.arity, _label(x.fn))
            start = len(self.items) - x.arity
            result = x.fn(*self.items[start:])
            del self.items[start:]
            self.items.append(result)
        elif isinstance(x, Cmd):
            self._need(x.needs, _label(x.fn))
            x.fn(self.items)
        else:
            self.items.append(x)
        return self

    def __rshift__(self, sink: Callable):
        self._need(1, "'>>'")
        sink(self.items[-1])
        self.items.pop()
        return self

    @property
    def peek(self) -> Any:
        self._need(1, "peek")
        return self.items[-1]

    def __len__(self) -> int:
        return len(self.items)

    def __repr__(self) -> str:
        return f"Stack({self.items})"
