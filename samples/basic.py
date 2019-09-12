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

    # noinspection PyMethodMayBeStatic
    def f(self):
        return 2


class BasicClass3:
    @staticmethod
    def a() -> Optional[int]:
        return 2
