from math import sqrt


class BasicClass:
    dimensions: int = 2

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def magnitude(self) -> float:
        return sqrt(self.x * self.x + self.y * self.y)
