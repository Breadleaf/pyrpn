import pytest

from pyrpn_lib import Stack, StackUnderflow, add, div, dup, mul, neg, sqrt, sub, swap


def test_sub_order():
    s = Stack() << 5 << 3 << sub
    assert s.items == [2]


def test_underflow_names_the_op():
    with pytest.raises(StackUnderflow, match="add needs 2"):
        Stack() << 1 << add


def test_failed_op_keeps_stack():
    s = Stack() << 1 << 0
    with pytest.raises(ZeroDivisionError):
        s << div
    assert s.items == [1, 0]


def test_swap_and_dup_underflow():
    with pytest.raises(StackUnderflow):
        Stack() << 1 << swap
    with pytest.raises(StackUnderflow):
        Stack() << dup


def test_extra_ops_and_peek():
    s = Stack() << 4 << neg
    assert s.items == [-4]

    s = Stack() << 9 << sqrt
    assert s.items == [3.0]

    s = Stack() << 2 << 3 << mul
    assert s.items == [6]

    assert s.peek == 6
    assert len(s) == 1


def test_rshift_sink():
    results = []
    s = Stack() << 43
    s >> results.append
    assert results == [43]
    assert len(s) == 0
