a: int = 3
b = "b"


def foo(x: str) -> int:
    return 3


class C:
    c: bool

    # noinspection PyMethodMayBeStatic
    def d(self, x: int, y: int) -> float:
        return float(x + y)
