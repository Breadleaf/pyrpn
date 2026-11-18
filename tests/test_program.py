import pytest

from pyrpn_lib import Stack, stack_function


def test_stack_function_validation():
    # missing type annotation
    with pytest.raises(TypeError, match="needs a type annotation"):

        @stack_function()
        def bad_1(s):
            pass

    # wrong parameter type
    with pytest.raises(TypeError, match="must be annotated pyrpn_lib.Stack"):

        @stack_function()
        def bad_2(s: int) -> None:
            pass

    # missing return annotation
    with pytest.raises(TypeError, match="missing return annotation"):

        @stack_function()
        def bad_3(s: Stack):
            pass

    # wrong return type annotation
    with pytest.raises(TypeError, match="must return None"):

        @stack_function()
        def bad_4(s: Stack) -> int:
            return 1

    # too many arguments
    with pytest.raises(TypeError, match="must accept exactly one argument"):

        @stack_function()
        def bad_5(s: Stack, extra: int) -> None:
            pass


def test_stack_function_contracts():
    @stack_function(requires=2, delta=1)
    def add_two(s: Stack) -> None:
        pass

    s = Stack() << 1 << 2
    with pytest.raises(RuntimeError, match="declared stack delta"):
        add_two.call(s)


def test_stack_function_rollback():
    @stack_function(requires=1)
    def crashing_func(s: Stack) -> None:
        s << 99
        raise ValueError("oops")

    s = Stack() << 5
    with pytest.raises(ValueError, match="oops"):
        crashing_func.call(s)

    assert s.items == [5]
