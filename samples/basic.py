from math import sqrt
from typing import Any, Optional


class BasicClass:
    __slots__ = ['x', 'y']
    dimensions: int = 2

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def magnitude(self) -> float:
        return sqrt(self.x * self.x + self.y * self.y)


class BasicClass2:
    a: Any
    b: Any = 3

    # noinspection PyMethodMayBeStatic
    def f(self):
        return 2


class BasicClass3:
    @staticmethod
    def a() -> Optional[int]:
        return 2


IntAlias = int


class BasicClass4:
    @property
    def p(self) -> int:
        return 3

    def f(self, x: IntAlias, y: IntAlias = 3):
        pass


class BasicClass5:
    def __add__(self, other: int) -> int:
        pass

    def __pos__(self) -> 'BasicClass5':
        pass
