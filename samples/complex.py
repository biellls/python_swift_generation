from typing import Union, overload


class ComplexClass1:
    def f(self, x: int, y: Union[int, float], z: float) -> float:
        pass


class ComplexClass2:
    @overload
    def f(self, x: int) -> int:
        ...

    @overload
    def f(self, x: float) -> float:
        ...

    # noinspection PyMethodMayBeStatic
    def f(self, x):
        return x + 2
