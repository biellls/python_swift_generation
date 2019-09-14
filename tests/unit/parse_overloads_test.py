from typing import Tuple

import pytest

from swift_python_wrapper.overload_parser import a_whitespace, ParseError, get_tk, a_str, a_id, a_typed_param, \
    a_get_type, a_typed_params, a_def, parse_overloads
from swift_python_wrapper.rendering import NameAndType, Function


def test_a_whitespace():
    i = a_whitespace(' \t\na\t', 0)
    assert get_tk(' \t\na\t', i) == 'a'
    assert i == 3
    with pytest.raises(ParseError):
        a_whitespace('a', 0)


def test_a_str():
    code = 'def abc():'
    i = a_str(code, 0, 'def')
    assert get_tk(code, i) == ' '
    assert i == 3
    with pytest.raises(ParseError):
        a_str(code, 0, 'deaf abc()')


def test_a_id():
    code = 'a3b_3c('
    identifier, i = a_id(code, 0)
    assert identifier == 'a3b_3c'
    assert get_tk(code, i) == '('
    assert i == 6
    with pytest.raises(ParseError):
        a_id('3ab = 2', 0)


def test_a_get_type():
    code = 'int,'
    t, i = a_get_type(code, 0)
    assert get_tk(code, i) == ','
    assert t == int
    code = 'Tuple[int, Tuple[int, float]],'
    t, i = a_get_type(code, 0)
    assert t == Tuple[int, Tuple[int, float]]


def test_a_typed_param():
    code = 'a: int, '
    nt, i = a_typed_param(code, 0)
    assert get_tk(code, i) == ','
    assert nt.name == 'a'
    assert nt.type == int
    code = 'a:Tuple[ float ,float ])'
    nt, i = a_typed_param(code, 0)
    assert get_tk(code, i) == ')'
    assert nt == NameAndType(name='a', type=Tuple[float, float])


def test_a_typed_params():
    code = 'a: float, b: Tuple[int, float], c: str)'
    tps, i = a_typed_params(code, 0)
    assert get_tk(code, i) == ')'
    assert tps == [NameAndType('a', float), NameAndType('b', Tuple[int, float]), NameAndType('c', str)]


def test_a_def():
    code = """def f(a: int, b: Tuple[float, int]) -> float: ..."""
    assert a_def('AClass', code) == Function(
        name='f',
        args=[NameAndType('a', int), NameAndType('b', Tuple[float, int])],
        cls='AClass',
        return_type=float,
    )

    code = """def f(a: int, b: Tuple[float, int]):
     ..."""
    assert a_def('AClass', code) == Function(
        name='f',
        args=[NameAndType('a', int), NameAndType('b', Tuple[float, int])],
        cls='AClass',
        return_type=None,
    )


def test_parse_overloads():
    code = """\
from typing import overload

@overload
def f(x: int) -> int: ...
@overload
def f(x: float) -> float: ...

class A:
    @overload
    def f(x: str) -> str:
        ...
        
    @overload
    def f(x: bool) -> bool:
        ...
"""
    assert parse_overloads(code, indentation=0, module_or_class_name='test_module') == [
        Function(
            name='f',
            args=[NameAndType('x', int)],
            cls='test_module',
            return_type=int
        ),
        Function(
            name='f',
            args=[NameAndType('x', float)],
            cls='test_module',
            return_type=float
        ),
    ]

    assert parse_overloads(code, indentation=1, module_or_class_name='A') == [
        Function(
            name='f',
            args=[NameAndType('x', str)],
            cls='A',
            return_type=str
        ),
        Function(
            name='f',
            args=[NameAndType('x', bool)],
            cls='A',
            return_type=bool
        ),
    ]

