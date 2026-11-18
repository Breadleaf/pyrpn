import inspect
from collections.abc import Callable
from typing import get_type_hints

from .stack import Stack, StackUnderflow

StackProgramType = Callable[[Stack], None]


def _validate_function(program: StackProgramType) -> None:
    """Raise TypeError if `program` isn't (Stack) -> None."""
    if not callable(program):
        raise TypeError(f"program must be callable; got {type(program).__name__}")

    name = getattr(program, "__name__", repr(program))

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
            f"program '{name}': parameter '{param.name}' needs a type annotation, expected pyrpn_lib.Stack"
        )
    if hints[param.name] is not Stack:
        raise TypeError(
            f"program '{name}': parameter '{param.name}' must be annotated pyrpn_lib.Stack; got {hints[param.name]!r}"
        )

    if "return" not in hints:
        raise TypeError(
            f"program '{name}': missing return annotation (expected -> None)"
        )
    if hints["return"] is not type(None):
        raise TypeError(
            f"program '{name}': must return None; annotated {hints['return']!r}"
        )


def _validate_stack_effect(requires: int, delta: int | None) -> None:
    """Validate a function's declared stack contract."""
    if isinstance(requires, bool) or not isinstance(requires, int):
        raise TypeError("requires must be an integer")
    if requires < 0:
        raise ValueError("requires cannot be negative")
    if delta is not None and (isinstance(delta, bool) or not isinstance(delta, int)):
        raise TypeError("delta must be an integer or None")


class StackFunction:
    """A (Stack) -> None routine that works on a stack the caller supplies."""

    def __init__(
        self, fn: StackProgramType, *, requires: int = 0, delta: int | None = None
    ) -> None:
        _validate_function(fn)
        _validate_stack_effect(requires, delta)
        self.fn = fn
        self.requires = requires
        self.delta = delta
        self.__name__ = getattr(fn, "__name__", repr(fn))
        self.__doc__ = getattr(fn, "__doc__", None)

    def call(self, stack: Stack) -> Stack:
        """Run the program on an existing stack and return that same stack."""

        if not isinstance(stack, Stack):
            raise TypeError(
                f"program '{self.__name__}' needs a stack; got {type(stack).__name__}"
            )

        if len(stack) < self.requires:
            raise StackUnderflow(
                f"{self.__name__} requires {self.requires} item(s), stack has {len(stack)}"
            )

        before = len(stack)
        snapshot = stack.items.copy()
        try:
            result = self.fn(stack)
            if result is not None:
                raise TypeError(
                    f"program '{self.__name__}' returned {result!r}, expected None"
                )
            if self.delta is not None:
                actual_delta = len(stack) - before
                if actual_delta != self.delta:
                    raise RuntimeError(
                        f"{self.__name__} declared stack delta {self.delta:+d}, "
                        f"but changed depth by {actual_delta:+d}"
                    )
        except Exception:
            stack.items[:] = snapshot
            raise
        return stack

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.__name__})"


def stack_function(
    *, requires: int = 0, delta: int | None = None
) -> Callable[[StackProgramType], StackFunction]:
    def deco(fn: StackProgramType) -> StackFunction:
        return StackFunction(fn, requires=requires, delta=delta)

    return deco


class StackProgram(StackFunction):
    """Wraps a (Stack) -> None function. Validated on creation; run with .run()."""

    def __init__(self, fn: StackProgramType) -> None:
        super().__init__(fn, requires=0, delta=None)

    def run(self, *, verbose: bool = True) -> Stack:
        if verbose:
            print(f"running program: {self.__name__}")
        s = self.call(Stack())
        if verbose:
            print(s)
        return s
