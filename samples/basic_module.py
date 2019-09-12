a: int = 3
b = "b"


def foo() -> int:
    return 3


class C:
    c: bool

    # noinspection PyMethodMayBeStatic
    def d(self):
        print("d")
