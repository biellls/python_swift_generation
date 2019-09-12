from typing import Any, Optional

from python_swift_generation.core import create_class_orm
from python_swift_generation.rendering import SwiftClass, NameAndType, Function
from samples.basic import BasicClass, BasicClass2, BasicClass3, BasicClass4


def test_simple_create_object_orm():
    assert create_class_orm(BasicClass) == SwiftClass(
        object_name='BasicClass',
        module='samples.basic',
        static_vars=[NameAndType(name='dimensions', type=int)],
        instance_vars=[NameAndType(name='x', type=None), NameAndType(name='y', type=None)],
        init_params=[NameAndType(name='x', type=float), NameAndType(name='y', type=float)],
        methods=[Function(name='magnitude', args=[], return_type=float, cls='instancemethod')],
    )


def test_simple_create_object_orm2():
    assert create_class_orm(BasicClass2) == SwiftClass(
        object_name='BasicClass2',
        module='samples.basic',
        static_vars=[NameAndType(name='b', type=Any)],
        instance_vars=[NameAndType(name='a', type=Any), NameAndType(name='b', type=Any)],
        init_params=[],
        methods=[Function(name='f', args=[], return_type=None, cls='instancemethod')],
    )


def test_simple_create_object_orm3():
    swift_obj = create_class_orm(BasicClass3)
    assert swift_obj == SwiftClass(
        object_name='BasicClass3',
        module='samples.basic',
        static_vars=[],
        instance_vars=[],
        init_params=[],
        methods=[Function(name='a', args=[], return_type=Optional[int], cls='staticmethod')],
    )
    assert swift_obj.methods[0].mapped_return_type == 'TPythonInt?'
