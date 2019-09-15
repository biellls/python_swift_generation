import inspect
import re
import sys
from copy import deepcopy
from importlib import util
from pathlib import Path
from types import SimpleNamespace
from typing import List, Union

from swift_python_wrapper.overload_parser import parse_overloads
from swift_python_wrapper.rendering import SwiftClass, NameAndType, Function, SwiftModule, _render, MagicMethods, \
    BinaryMagicMethod, UnaryMagicMethod, ExpressibleByLiteralProtocol


class BrokenImportError(Exception):
    pass


def build_swift_wrappers_module(module_name, module_path, target_dir):
    modules = [
        load_module_from_path(
            module_name=module_name or Path(module_path).stem,
            module_path=module_path,
        )
    ] if Path(module_path).is_file() else [
        load_module_from_path(
            module_name=Path(path).stem,
            module_path=str(path),
        )
        for path in Path(module_path).iterdir() if path.is_file()
    ]
    create_typed_python([create_module_orm(module) for module in modules], target_path=target_dir)


def load_module_from_path(module_name: str, module_path: str):
    spec = util.spec_from_file_location(module_name, module_path)
    module = util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        sys.modules[module_name] = module
    except (NameError, SyntaxError):
        raise BrokenImportError(f'Error loading module {module_path}')
    return module


def get_module_classes(module) -> List[SwiftClass]:
    return [create_class_orm(obj) for name, obj in inspect.getmembers(module) if inspect.isclass(obj) and obj.__module__ == module.__name__ and can_get_source(obj)]


def can_get_source(obj) -> bool:
    try:
        inspect.getsource(obj)
        return True
    except OSError:
        return False


def get_module_functions(module) -> List[Function]:
    functions = [
        Function(
            name=func.__name__,
            args=[NameAndType(name=k, type=v) for k, v in func.__annotations__.items() if k != 'return'],
            cls='modulefunction',
            return_type=func.__annotations__.get('return'),
        )
        for func in
        [obj[1] for obj in inspect.getmembers(module) if inspect.isfunction(obj[1]) and not obj[1].__name__ in ['overload', '_overload_dummy']]
    ]
    overloads = get_overloads(module, is_module=True)
    functions = [x for x in functions if x.name not in {f.name for f in overloads}] + overloads
    return flatten_functions(functions)


def create_module_orm(module) -> SwiftModule:
    return SwiftModule(
        module_name=module.__name__,
        vars=[NameAndType(name=k, type=v) for k, v in getattr(module, '__annotations__', {}).items()],
        functions=get_module_functions(module),
        classes=get_module_classes(module)
    )


def is_static_method(cls, name: str) -> bool:
    return cls.__dict__[name].__class__ == staticmethod or cls.__dict__[name].__class__ == classmethod


def get_functions(cls) -> List[Function]:
    functions = [
        Function(
            name=func_name,
            args=[
                NameAndType(name=k, type=v.annotation, default_value=v.default)
                for k, v in inspect.signature(func).parameters.items()
                if k != 'return' and k != 'self'
            ],
            cls='staticmethod' if is_static_method(cls, func_name) else 'instancemethod',
            return_type=func.__annotations__.get('return'),
        )
        for func_name, func in
        [
            (func_name, func)
            for func_name, func in inspect.getmembers(cls, lambda x: inspect.isfunction(x) or inspect.ismethod(x))
            if not func_name.startswith("__") and func_name not in ['overload', '_overload_dummy']
        ]
    ]
    overloads = get_overloads(cls, is_module=False)
    functions = [x for x in functions if x.name not in {f.name for f in overloads}] + overloads
    return flatten_functions(functions)


def flatten_functions(functions) -> List[Function]:
    result = []
    for f in functions:
        flattened_args = [[]]
        for arg in f.args:
            if arg.type.__class__ == type(Union):
                new_flattened_args = []
                for t in arg.type.__args__:
                    flattened_args_copy = deepcopy(flattened_args)
                    for l in flattened_args_copy:
                        l.append(NameAndType(arg.name, t))
                    new_flattened_args = new_flattened_args + flattened_args_copy
                flattened_args = new_flattened_args
            else:
                for l in flattened_args:
                    l.append(arg)
        for l in flattened_args:
            result.append(Function(name=f.name, args=l, cls=f.cls, return_type=f.return_type))
    return result


binary_magic_mappings = {
    '__add__': ('+', None, float),
    '__sub__': ('-', None, float),
    '__mul__': ('*', None, float),
    '__div__': ('/', None, float),
    '__mod__': ('%', None, float),
    '__lshift__': ('<<', None, float),
    '__rshift__': ('>>', None, float),
    '__iadd__': ('+=', None, float),
    '__isub__': ('-=', None, float),
    '__imul__': ('*=', None, float),
    '__idiv__': ('/=', None, float),
}

unary_magic_mappings = {
    '__pos__': ('+', None, float),
    '__neg__': ('-', None, float),
}

expressible_by_literal_protocols = {
    'ExpressibleByIntegerLiteral': 'Int',
    'ExpressibleByFloatLiteral': 'Double',
    'ExpressibleByBooleanLiteral': 'Bool',
    'ExpressibleByStringLiteral': 'String',
}


def get_magic_methods(cls) -> MagicMethods:
    magic_methods = {}
    for func in [inspect.getattr_static(cls, func) for func in dir(cls) if callable(inspect.getattr_static(cls, func)) and func.startswith("__")]:
        if func.__name__ in binary_magic_mappings.keys():
            signature = inspect.signature(func)
            symbol, protocol, default_type = binary_magic_mappings[func.__name__]
            rhs = list(signature.parameters.items())[1][1].annotation
            return_value = signature.return_annotation if signature.return_annotation != inspect.Parameter.empty else None
            magic_methods[func.__name__.lstrip('_')] = BinaryMagicMethod(
                symbol=symbol,
                python_magic_method=func.__name__,
                swift_protocol_name=protocol,
                right_classes=[(rhs, return_value or default_type)]
            )
        elif func.__name__ in unary_magic_mappings.keys():
            symbol, protocol, default_type = unary_magic_mappings[func.__name__]
            magic_methods[func.__name__.lstrip('_')] = UnaryMagicMethod(
                symbol=symbol,
                python_magic_method=func.__name__,
                swift_protocol_name=protocol,
            )
        elif func.__name__ == '__len__':
            magic_methods[func.__name__.lstrip('_')] = True
        elif func.__name__ == '__getitem__':
            signature = inspect.signature(func)
            magic_methods[func.__name__.lstrip('_')] = SimpleNamespace(
                index_type=list(signature.parameters.items())[1][1].annotation,
                return_type=signature.return_annotation if signature.return_annotation != inspect.Parameter.empty else None,
            )
        elif func.__name__ == '__setitem__':
            magic_methods[func.__name__.lstrip('_')] = True

    for protocol_name in get_swift_wrapper_annotations(cls):
        if protocol_name in expressible_by_literal_protocols.keys():
            magic_methods[protocol_name] = ExpressibleByLiteralProtocol(
                protocol_name=protocol_name,
                literal_type=expressible_by_literal_protocols[protocol_name],
            )

    return MagicMethods(**magic_methods)


def get_swift_wrapper_annotations(cls) -> List[str]:
    result = []
    for line in inspect.getsource(cls).splitlines(keepends=False):
        for match in re.finditer(r'#\s*SWIFT_WRAPPER(\.\w+):\s*(\w+(?:\s*,\s*\w+)?)', inspect.getsource(cls)):
            annotated_class, protocols = match.groups()
            result += [x.strip() for x in protocols.split(',')]
    return result


def get_init_params(cls) -> List[List[NameAndType]]:
    params = [NameAndType(name=k, type=v) for k, v in inspect.getfullargspec(cls.__init__).annotations.items()]
    flattened_params = flatten_functions([Function(name='__init__', args=params, cls=cls.__name__)])
    return [x.args for x in flattened_params]


def create_class_orm(cls) -> SwiftClass:
    static_vars = [NameAndType(name=k, type=v) for k, v in getattr(cls, '__annotations__', {}).items() if getattr(cls, k, False)]
    instance_vars = \
        [NameAndType(name=x, type=None) for x in cls.__slots__] if hasattr(cls, '__slots__') else [] + \
        [NameAndType(name=k, type=v) for k, v in getattr(cls, '__annotations__', {}).items()] + \
        [NameAndType(name, type=getattr(prop.fget, '__annotations__', {}).get('return')) for name, prop in inspect.getmembers(cls, lambda o: isinstance(o, property))]
    init_params = get_init_params(cls)
    return SwiftClass(
        object_name=cls.__name__,
        module=cls.__module__,
        static_vars=static_vars,
        instance_vars=instance_vars,
        init_params=init_params,
        methods=get_functions(cls),
        magic_methods=get_magic_methods(cls),
    )


def get_overloads(module_or_class, is_module: bool = False):
    indents = 0 if is_module else 1
    return parse_overloads(inspect.getsource(module_or_class), indentation=indents, module_or_class_name=module_or_class.__name__)


def create_typed_python(modules: List[SwiftModule], target_path: str):
    for module in modules:
        code = module.render()
        (Path(target_path) / f'{module.swift_module_name}.swift').write_text(code)
    code = _render('typed_python.swift.j2', {'modules': modules})
    (Path(target_path) / f'typed_python.swift').write_text(code)


if __name__ == '__main__':
    build_swift_wrappers_module(
        module_name=None,
        module_path='/Users/biellls/Development/Python/python_swift_generation/stubs',
        target_dir='/Users/biellls/Development/Python/python_swift_generation/aout'
    )
