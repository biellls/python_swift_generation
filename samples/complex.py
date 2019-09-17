from typing import Union, overload, List, Generic, TypeVar, Tuple


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
    # SWIFT_WRAPPER.ComplexClass3: ExpressibleByIntegerLiteral, ExpressibleByFloatLiteral, CPython
    def foo(self, x: List[str]) -> List[str]:
        pass


T = TypeVar('T')
V = TypeVar('V')


class ComplexClass4(Generic[T]):
    a: int
    b: T

    def __init__(self, a: int, b: T):
        self.a = a
        self.b = b

    @property
    def shape(self) -> Tuple[int, T]:
        return self.a, self.b

    # noinspection PyMethodMayBeStatic
    def identity(self, val: V) -> V:
        return val
