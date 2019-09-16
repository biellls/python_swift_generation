from typing import Tuple

from swift_python_wrapper.rendering import Function


def test_wrapped_return():
    assert Function(
        name='foo',
        args=[],
        cls='A',
        return_type=Tuple[int, float]
    ).wrapped_return == '(TPint(val.0), TPfloat(val.1))'