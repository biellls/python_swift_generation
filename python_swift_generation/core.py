import inspect
from importlib import util

from python_swift_generation.rendering import SwiftObject, NameAndType, Function


class BrokenImportError(Exception):
    pass


def load_module_from_path(module_name: str, module_path: str):
    spec = util.spec_from_file_location(module_name, module_path)
    module = util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except (NameError, SyntaxError):
        raise BrokenImportError(f'Error loading module {module_path}')
    return module


def get_module_classes(module):
    pass


def get_module_functions(module):
    pass


def get_user_attributes(cls):
    excluded = dir(type('dummy', (object,), {}))
    return [item
            for item in inspect.getmembers(cls)
            if item[0] not in excluded]


def create_class_orm(cls) -> SwiftObject:
    static_vars = [NameAndType(name=k, type=v.__name__) for k, v in cls.__annotations__.items()]
    instance_vars = [NameAndType(name=x, type=None) for x in cls.__slots__] if hasattr(cls, '__slots__') else []
    instance_methods = [
        Function(name=func.__name__, args=[], return_type=func.__annotations__.get('return').__name__)
        for func in
        [getattr(cls, func) for func in dir(cls) if callable(getattr(cls, func)) and not func.startswith("__")]]
    init_params = [NameAndType(name=k, type=v.__name__) for k, v in inspect.getfullargspec(cls.__init__).annotations.items()]
    return SwiftObject(
        object_name=cls.__name__,
        module=cls.__module__,
        static_vars=static_vars,
        instance_vars=instance_vars,
        init_params=init_params,
        instance_methods=instance_methods
    )
