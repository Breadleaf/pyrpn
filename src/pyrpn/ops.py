import math
import operator
from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class Op:
    fn: Callable
    arity: int

add = Op(operator.add, 2)
sub = Op(operator.sub, 2)
mul = Op(operator.mul, 2)
div = Op(operator.truediv, 2)
neg = Op(operator.neg, 1)
sqrt = Op(math.sqrt, 1)

@dataclass(frozen=True)
class Cmd:
    fn: Callable[[list], None]
    needs: int = 0 # minimum stack depth

def _swap(items):
    items[-1], items[-2] = items[-2], items[-1]

def _dup(items):
    items.append(items[-1])

swap = Cmd(_swap, 2)
dup = Cmd(_dup, 1)
