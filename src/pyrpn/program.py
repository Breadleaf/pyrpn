import inspect
from collections.abc import Callable
from typing import get_type_hints

from .stack import Stack, StackUnderflow

StackProgramType = Callable[[Stack], None]


def _validate_function(program: StackProgramType) -> None:
    """Raise TypeError if `fn` isn't (Stack) -> None."""
    if not callable(program):
        raise TypeError(f"program must be callable; got {type(program).__name__}")

    name = getattr(program, __name__, repr(program))

    params = list(inspect.signature(program).parameters.values())
    if len(params) != 1:
        raise TypeError(
            f"program: '{name}' must accept exactly one argument; found {len(params)}"
        )

    param = params[0]
    if param.kind not in (param.POSITIONAL_ONLY, param.POSITIONAL_OR_KEYWORD):
        raise TypeError(
            f"program '{name}': its argument must be a plain positional parameter"
        )

    try:
        hints = get_type_hints(program)
    except Exception as ex:
        raise TypeError(
            f"program '{name}': could not resolve annotations: {ex}"
        ) from ex

    if param.name not in hints:
        raise TypeError(
            f"program '{name}': parameter '{param.name}' needs a type annotation, expected pyrpn.Stack"
        )
    if hints[param.name] is not Stack:
        raise TypeError(
            f"program '{name}': parameter '{param.name}' must be annotated pyrpn.Stack; got {hints[param.name]!r}"
        )

    if "return" not in hints:
        raise TypeError(
            f"program '{name}': missing return annotation (expected -> None)"
        )
    if hints["return"] is not type(None):
        raise TypeError(
            f"program '{name}': must return None; annotated {hints['return']!r}"
        )


class StackFunction:
    """A (Stack) -> None routine that works on a stack the caller supplies."""

    def __init__(
        self, fn: StackProgramType, *, takes: int = 0, returns: int | None = None
    ) -> None:
        _validate_function(fn)
        self.fn = fn
        self.takes = takes
        self.returns = returns
        self.__name__ = getattr(fn, "__name__", repr(fn))
        self.__doc__ = fn.__doc__

    def call(self, stack: Stack) -> Stack:
        """Run the program on an existing stack and return that same stack."""

        if not isinstance(stack, Stack):
            raise TypeError(
                f"program '{self.__name__}' needs a stack; got {type(stack).__name__}"
            )

        if len(stack) < self.takes:
            raise StackUnderflow(
                f"{self.__name__} takes {self.takes} items(s), stack has {len(stack)}"
            )

        before = len(stack)
        snapshot = stack.items.copy()
        try:
            result = self.fn(stack)
            if result is not None:
                raise TypeError(
                    f"program '{self.__name__}' returned {result!r}, expected None"
                )
            if self.returns is not None:
                expected = before - self.takes + self.returns
                if len(stack) != expected:
                    raise RuntimeError(
                        f"{self.__name__} declared ({self.takes} -> {self.returns}) "
                        f"but left {len(stack)} item(s), expected {expected}"
                    )
        except Exception:
            stack.items[:] = snapshot
            raise
        return stack

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.__name__})"


def stack_function(*, takes: int = 0, returns: int | None = None) -> Callable[[StackProgramType], StackFunction]:
    def deco(fn: StackProgramType) -> StackFunction:
        return StackFunction(fn, takes=takes, returns=returns)

    return deco


class StackProgram(StackFunction):
    """Wraps a (Stack) -> None function. Validated on creation; run with .run()."""

    def __init__(self, fn: StackProgramType) -> None:
        super().__init__(fn, takes=0)

    def run(self, *, verbose: bool = True) -> Stack:
        if verbose:
            print(f"running program: {self.__name__}")
        s = self.call(Stack())
        if verbose:
            print(s)
        return s
