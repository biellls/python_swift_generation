from typing import Any, Optional, List

import mock

from samples.complex import ComplexClass1, ComplexClass2, ComplexClass3
from swift_python_wrapper.core import create_class_orm
from swift_python_wrapper.rendering import SwiftClass, NameAndType, Function, MagicMethods, BinaryMagicMethod, \
    UnaryMagicMethod, ExpressibleByLiteralProtocol
from samples.basic import BasicClass, BasicClass2, BasicClass3, BasicClass4, BasicClass5


def test_simple_create_object_orm():
    assert create_class_orm(BasicClass) == SwiftClass(
        object_name='BasicClass',
        module='samples.basic',
        static_vars=[NameAndType(name='dimensions', type=int)],
        instance_vars=[NameAndType(name='x', type=None), NameAndType(name='y', type=None)],
        init_params=[[NameAndType(name='x', type=float), NameAndType(name='y', type=float)]],
        methods=[Function(name='magnitude', args=[], return_type=float, cls='instancemethod')],
        magic_methods=mock.ANY,
    )


def test_simple_create_object_orm2():
    assert create_class_orm(BasicClass2) == SwiftClass(
        object_name='BasicClass2',
        module='samples.basic',
        static_vars=[NameAndType(name='b', type=Any)],
        instance_vars=[NameAndType(name='a', type=Any), NameAndType(name='b', type=Any)],
        init_params=[[]],
        methods=[Function(name='f', args=[], return_type=None, cls='instancemethod')],
        magic_methods=mock.ANY,
    )


def test_simple_create_object_orm3():
    swift_obj = create_class_orm(BasicClass3)
    assert swift_obj == SwiftClass(
        object_name='BasicClass3',
        module='samples.basic',
        static_vars=[],
        instance_vars=[],
        init_params=[[]],
        methods=[Function(name='a', args=[], return_type=Optional[int], cls='staticmethod')],
        magic_methods=mock.ANY,
    )
    assert swift_obj.methods[0].mapped_return_type == 'TPint?'


def test_simple_create_object_orm4():
    swift_obj = create_class_orm(BasicClass4)
    assert swift_obj == SwiftClass(
        object_name='BasicClass4',
        module='samples.basic',
        static_vars=[],
        instance_vars=[NameAndType('p', int)],
        init_params=[[]],
        methods=[Function(name='f', args=[NameAndType('x', int), NameAndType('y', int, 3)], return_type=None, cls='instancemethod')],
        magic_methods=mock.ANY,
    )


def test_simple_create_object_orm5():
    swift_obj = create_class_orm(BasicClass5)
    assert swift_obj == SwiftClass(
        object_name='BasicClass5',
        module='samples.basic',
        static_vars=[],
        instance_vars=[],
        init_params=[[]],
        methods=[],
        magic_methods=mock.ANY,
    )
    assert BinaryMagicMethod(symbol='+', python_magic_method='__add__', swift_protocol_name=None, right_classes=[(int, int)]) in swift_obj.magic_methods.binary_magic_methods
    assert swift_obj.magic_methods.unary_magic_methods == [UnaryMagicMethod(symbol='+', python_magic_method='__pos__', swift_protocol_name=None)]


def test_complex_create_object_orm1():
    swift_obj = create_class_orm(ComplexClass1)
    assert swift_obj == SwiftClass(
        object_name='ComplexClass1',
        module='samples.complex',
        static_vars=[],
        instance_vars=[],
        init_params=[[]],
        methods=[
            Function(name='f', args=[NameAndType('x', int), NameAndType('y', int), NameAndType('z', float)], return_type=float, cls='instancemethod'),
            Function(name='f', args=[NameAndType('x', int), NameAndType('y', float), NameAndType('z', float)], return_type=float, cls='instancemethod'),
        ],
        magic_methods=mock.ANY,
    )


def test_complex_create_object_orm3():
    swift_obj = create_class_orm(ComplexClass3)
    assert swift_obj == SwiftClass(
        object_name='ComplexClass3',
        module='samples.complex',
        static_vars=[],
        instance_vars=[],
        init_params=[[]],
        methods=[
            Function(name='foo', args=[NameAndType('x', List[str])], return_type=List[str], cls='instancemethod'),
        ],
        magic_methods=mock.ANY,
    )
    assert swift_obj.methods[0].mapped_return_type == 'TPList<TPstr>'
    assert swift_obj.magic_methods.expressible_by_literals == [
        ExpressibleByLiteralProtocol('ExpressibleByIntegerLiteral', literal_type='Int'),
        ExpressibleByLiteralProtocol('ExpressibleByFloatLiteral', literal_type='Double'),
    ]
