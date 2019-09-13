import math
from typing import Optional


class Vector2D:
    dimensions: int = 2
    x: float
    y: float

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def magnitude(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y)

    def add(self, scalar: float = 1) -> 'Vector2D':
        return Vector2D(self.x + scalar, self.y + scalar)

    def add_if_even(self, scalar: float) -> Optional['Vector2D']:
        if math.floor(scalar) % 2 == 0:
            return Vector2D(self.x + scalar, self.y + scalar)
        else:
            return None
