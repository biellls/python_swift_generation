from typing import Union, overload, List


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


class ComplexClass3:
    def foo(self, x: List[str]) -> List[str]:
        pass
