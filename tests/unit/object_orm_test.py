from python_swift_generation.core import create_class_orm
from python_swift_generation.rendering import SwiftObject, NameAndType, Function
from samples.basic import BasicClass


def test_simple_create_object_orm():
    assert create_class_orm(BasicClass) == SwiftObject(
        object_name='BasicClass',
        module='samples.basic',
        static_vars=[NameAndType(name='dimensions', type='int')],
        instance_vars=[NameAndType(name='x', type=None), NameAndType(name='y', type=None)],
        init_params=[NameAndType(name='x', type='float'), NameAndType(name='y', type='float')],
        instance_methods=[Function(name='magnitude', args=[], return_type='float')]
    )
