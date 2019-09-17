from typing import Union, overload, List, Generic, TypeVar


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
    # SWIFT_WRAPPER.ComplexClass3: ExpressibleByIntegerLiteral, ExpressibleByFloatLiteral
    def foo(self, x: List[str]) -> List[str]:
        pass


T = TypeVar('T')
V = TypeVar('V')


class ComplexClass4(Generic[T]):
    # SWIFT_WRAPPER.ComplexClass4: CPython
    def foo(self, x: T, y: V) -> V:
        pass
