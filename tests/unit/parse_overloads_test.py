from typing import Tuple

import pytest

from swift_python_wrapper.overload_parser import a_whitespace, ParseError, get_tk, a_str, a_id, a_typed_param, \
    a_get_type, a_typed_params
from swift_python_wrapper.rendering import NameAndType


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
