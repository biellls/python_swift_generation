from swift_python_wrapper.core import create_module_orm
from swift_python_wrapper.rendering import SwiftModule, NameAndType, Function, SwiftClass
from samples import basic_module


def test_basic_module_orm():
    module = create_module_orm(basic_module)
    assert module == SwiftModule(
        module_name='samples.basic_module',
        vars=[NameAndType(name='a', type=int)],
        functions=[Function(name='foo', args=[NameAndType('x', str)], cls='modulefunction', return_type=int)],
        classes=[SwiftClass(
            object_name='C',
            module='samples.basic_module',
            static_vars=[],
            instance_vars=[NameAndType(name='c', type=bool)],
            init_params=[],
            methods=[Function(name='d', args=[NameAndType('x', int), NameAndType('y', int)], cls='instancemethod', return_type=float)]
        )]
    )
