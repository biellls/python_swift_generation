import inspect
from importlib import util
from typing import List

from python_swift_generation.rendering import SwiftClass, NameAndType, Function, SwiftModule, _render


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


def get_module_classes(module) -> List[SwiftClass]:
    return [create_class_orm(obj) for name, obj in inspect.getmembers(module) if inspect.isclass(obj)]


def get_module_functions(module) -> List[Function]:
    return [
        Function(
            name=func.__name__,
            args=[NameAndType(name=k, type=v) for k, v in func.__annotations__.items() if k != 'return'],
            cls='modulefunction',
            return_type=func.__annotations__.get('return'),
        )
        for func in
        [obj[1] for obj in inspect.getmembers(module) if inspect.isfunction(obj[1])]
    ]


def create_module_orm(module) -> SwiftModule:
    return SwiftModule(
        module_name=module.__name__,
        vars=[NameAndType(name=k, type=v) for k, v in getattr(module, '__annotations__', {}).items()],
        functions=get_module_functions(module),
        classes=get_module_classes(module)
    )


def is_static_method(cls, name: str) -> bool:
    return cls.__dict__[name].__class__ == staticmethod


def get_functions(cls) -> List[Function]:
    return [
        Function(
            name=func.__name__,
            args=[
                NameAndType(name=k, type=v.annotation, default_value=v.default)
                for k, v in inspect.signature(func).parameters.items()
                if k != 'return'
            ],
            cls='staticmethod' if is_static_method(cls, func.__name__) else 'instancemethod',
            return_type=func.__annotations__.get('return'),
        )
        for func in
        [getattr(cls, func) for func in dir(cls) if callable(getattr(cls, func)) and not func.startswith("__")]
    ]


def create_class_orm(cls) -> SwiftClass:
    static_vars = [NameAndType(name=k, type=v) for k, v in getattr(cls, '__annotations__', {}).items() if getattr(cls, k, False)]
    instance_vars = \
        [NameAndType(name=x, type=None) for x in cls.__slots__] if hasattr(cls, '__slots__') else [] + \
        [NameAndType(name=k, type=v) for k, v in getattr(cls, '__annotations__', {}).items()]
    init_params = [NameAndType(name=k, type=v) for k, v in inspect.getfullargspec(cls.__init__).annotations.items()]
    return SwiftClass(
        object_name=cls.__name__,
        module=cls.__module__,
        static_vars=static_vars,
        instance_vars=instance_vars,
        init_params=init_params,
        methods=get_functions(cls),
    )


def create_typed_python(modules: List[SwiftModule], target_path: str):
    for module in modules:
        code = module.render()
        (Path(target_path) / f'{module.swift_module_name}.swift').write_text(code)
    code = _render('typed_python.swift.j2', {'modules': modules})
    (Path(target_path) / f'typed_python.swift').write_text(code)


if __name__ == '__main__':
    from pathlib import Path
    import sys
    sys.path.append(str(Path(__file__).parent.parent / 'samples'))
    import mathy

    mod = create_module_orm(mathy)
    create_typed_python([mod], '/Users/biellls/Development/Swift/chip8/Sources/chip8/')
