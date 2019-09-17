import inspect
from pathlib import Path
from typing import NamedTuple, List, Optional, Any, Union, _ForwardRef, Tuple, Sequence, Generic, TypeVar, GenericMeta

import jinja2 as jinja2


class NameAndType(NamedTuple):
    name: str
    type: Optional[type]
    default_value: Any = inspect.Parameter.empty

    @property
    def mapped_default_value(self):
        if self.default_value in [True, False]:
            return str(self.default_value).lower()
        elif self.default_value is None:
            return 'nil'
        elif isinstance(self.default_value, str):
            return f'"{self.default_value}"'
        else:
            return self.default_value

    @property
    def mapped_type(self):
        return _convert_to_swift_type(self.type)

    @property
    def has_default_value(self):
        return self.default_value != inspect.Parameter.empty

    @property
    def wrapped_instance(self):
        if self.type.__class__ == type(Tuple):
            return f'PythonObject({self.name})'
        else:
            return f'{self.name}.wrappedInstance'

    def _wrapped_return(self, wrapped: str) -> str:
        if self.type.__class__ == type(Tuple):
            n = len(self.type.__args__)
            converted = [f'{_convert_to_swift_type(x)}({wrapped}[dynamicMember: "{self.name}"].tuple{n}.{i})' for i, x in enumerate(self.type.__args__)]
            wrapped = f'({", ".join(converted)})'
            return wrapped
        else:
            return f'{self.mapped_type}({wrapped}[dynamicMember: "{self.name}"])'

    @property
    def wrapped_return(self):
        return self._wrapped_return('wrappedInstance')

    @property
    def wrapped_return_static(self):
        return self._wrapped_return('wrappedClass')

    @property
    def wrapped_return_module(self):
        return self._wrapped_return('wrappedModule')


class Function(NamedTuple):
    name: str
    args: List[NameAndType]
    cls: str
    return_type: Optional[type] = None

    @property
    def mapped_return_type(self):
        return _convert_to_swift_type(self.return_type)

    @property
    def tuple_return(self) -> str:
        if self.return_type.__class__ == type(Tuple):
            return f'.tuple{len(self.return_type.__args__)}'
        else:
            return ''

    def render_type_vars(self):
        type_vars = [x.type for x in self.args if x.type.__class__ == TypeVar]
        return f'<{", ".join([f"{x.__name__}: TPobject" for x in type_vars])}>' if type_vars != [] else ''

    @property
    def static_method(self):
        return self.cls == 'staticmethod'

    @property
    def instance_method(self):
        return self.cls == 'instancemethod'

    @property
    def module_function(self):
        return self.cls == 'modulefunction'

    @property
    def wrapped_return(self) -> str:
        if self.return_type.__class__ == type(Tuple):
            converted = [f'{_convert_to_swift_type(x)}(val.{i})' for i, x in enumerate(self.return_type.__args__)]
            wrapped = f'({", ".join(converted)})'
            return wrapped
        elif self.return_type.__class__ == TypeVar:
            return f'{self.mapped_return_type}.init(val)'
        else:
            return f'{self.mapped_return_type}(val)'


class SwiftClass(NamedTuple):
    object_name: str
    module: str
    static_vars: List[NameAndType]
    instance_vars: List[NameAndType]
    init_params: List[List[NameAndType]]
    methods: List[Function]
    magic_methods: 'MagicMethods'
    positional_args: bool = False
    generic: Optional[type] = None

    @property
    def swift_object_name(self):
        return f'TP{self.object_name}'

    @property
    def python_module_name(self):
        return self.module.replace('.stub', '')

    @property
    def type_vars(self) -> Optional[List[str]]:
        return None if self.generic is None else self.generic.__parameters__

    @property
    def as_dict(self):
        return dict(swift_object_name=self.swift_object_name, python_module_name=self.python_module_name, **self._asdict())

    def render_type_vars(self):
        if self.generic is not None:
            return f'<{", ".join([f"{x.__name__}: TPobject" for x in self.type_vars])}>'
        else:
            return ''

    def render_magic_methods(self):
        return _render('magic_methods.swift.j2', self.as_dict)

    def render(self):
        return _render('object.swift.j2', dict(
            rendered_magic_methods=self.render_magic_methods(),
            rendered_type_vars=self.render_type_vars(),
            **self.as_dict,
        ))


class SwiftModule(NamedTuple):
    module_name: str
    vars: List[NameAndType]
    functions: List[Function]
    classes: List[SwiftClass]

    @property
    def swift_module_name(self):
        return f'TPythonModule_{self.module_name.replace(".", "_")}'

    @property
    def python_module_name(self):
        return self.module_name.replace('.stub', '')

    @property
    def as_dict(self):
        return dict(swift_class_name=self.swift_module_name, python_module_name=self.python_module_name, **self._asdict())

    def render(self):
        return _render('module.swift.j2', self.as_dict)


def _convert_to_swift_type(python_type) -> str:
    if python_type == Any or python_type == type(None) or python_type == inspect.Parameter.empty:
        return 'TPobject'
    elif isinstance(python_type, str):
        return f'TP{python_type}'
    elif python_type.__class__ == type(Union) and python_type.__args__[1] == type(None):
        return _convert_to_swift_type(python_type.__args__[0]) + '?'
    elif python_type.__class__ == TypeVar:
        return python_type.__name__
    elif python_type.__class__ == type(Tuple):
        args = [_convert_to_swift_type(x) for x in python_type.__args__]
        return f'({", ".join(args)})'
    elif python_type.__class__ == GenericMeta:
        return f'TP{python_type.__name__}<{_convert_to_swift_type(python_type.__args__[0])}>'
    elif python_type.__class__ == type(Sequence):
        return f'TPSequence<{_convert_to_swift_type(python_type.__args__[0])}>'
    elif isinstance(python_type, _ForwardRef):
        return f'TP{python_type.__forward_arg__}'
    try:
        return f'TP{python_type.__name__}'
    except AttributeError:
        raise


class BinaryMagicMethod(NamedTuple):
    symbol: str
    python_magic_method: str
    swift_protocol_name: Optional[str]
    right_classes: List[Tuple[type, type]]  # List of right hand side types and return types for each


class UnaryMagicMethod(NamedTuple):
    symbol: str
    python_magic_method: str
    swift_protocol_name: Optional[str]


class ExpressibleByLiteralProtocol(NamedTuple):
    protocol_name: str
    literal_type: str

    @property
    def label_name(self) -> str:
        mappings = {
            'Double': 'floatLiteral',
            'Int': 'integerLiteral',
            'String': 'stringLiteral',
            'Bool': 'booleanLiteral',
            'Array': 'arrayLiteral',
        }
        return mappings[self.literal_type]


class MagicMethods(NamedTuple):
    # Equality
    eq__: Union[bool, BinaryMagicMethod] = False
    ne__: Union[bool, BinaryMagicMethod] = False
    gt__: Union[bool, BinaryMagicMethod] = False
    lt__: Union[bool, BinaryMagicMethod] = False
    ge__: Union[bool, BinaryMagicMethod] = False
    le__: Union[bool, BinaryMagicMethod] = False
    # Numeric
    pos__: Union[bool, UnaryMagicMethod] = False
    neg__: Union[bool, UnaryMagicMethod] = False
    add__: Union[bool, BinaryMagicMethod] = False
    sub__: Union[bool, BinaryMagicMethod] = False
    mul__: Union[bool, BinaryMagicMethod] = False
    truediv__: Union[bool, BinaryMagicMethod] = False
    mod__: Union[bool, BinaryMagicMethod] = False
    lshift__: Union[bool, BinaryMagicMethod] = False
    rshift__: Union[bool, BinaryMagicMethod] = False
    iadd__: Union[bool, BinaryMagicMethod] = False
    isub__: Union[bool, BinaryMagicMethod] = False
    imul__: Union[bool, BinaryMagicMethod] = False
    idiv__: Union[bool, BinaryMagicMethod] = False
    # Boolean
    and__: Union[bool, BinaryMagicMethod] = False
    or__: Union[bool, BinaryMagicMethod] = False
    xor__: Union[bool, BinaryMagicMethod] = False
    # Sequences
    len__: bool = False
    getitem__: bool = False
    setitem__: bool = False
    iter__: bool = False
    # Others
    context_manager: bool = False
    # Literal expressible protocols
    ExpressibleByIntegerLiteral: Union[bool, ExpressibleByLiteralProtocol] = False
    ExpressibleByFloatLiteral: Union[bool, ExpressibleByLiteralProtocol] = False
    ExpressibleByStringLiteral: Union[bool, ExpressibleByLiteralProtocol] = False
    ExpressibleByBooleanLiteral: Union[bool, ExpressibleByLiteralProtocol] = False
    ExpressibleByArrayLiteral: Union[bool, ExpressibleByLiteralProtocol] = False

    @property
    def unary_magic_methods(self) -> List[UnaryMagicMethod]:
        result = []
        for v in self._asdict().values():
            if isinstance(v, UnaryMagicMethod):
                result.append(v)
        return result

    @property
    def binary_magic_methods(self) -> List[BinaryMagicMethod]:
        result = []
        for v in self._asdict().values():
            if isinstance(v, BinaryMagicMethod):
                result.append(v)
        return result

    @property
    def expressible_by_literals(self) -> List[ExpressibleByLiteralProtocol]:
        result = []
        for v in self._asdict().values():
            if isinstance(v, ExpressibleByLiteralProtocol) and v.protocol_name != 'ExpressibleByArrayLiteral':
                result.append(v)
        return result


def _render(template_name: str, context: dict):
    search_path = Path(__file__).parent / 'templates'
    template_loader = jinja2.FileSystemLoader(searchpath=str(search_path))
    template_env = jinja2.Environment(loader=template_loader)

    template_env.trim_blocks = True
    template_env.lstrip_blocks = True
    template_env.keep_trailing_newline = True

    template_env.filters.update(convert_to_swift_type=_convert_to_swift_type)

    template = template_env.get_template(template_name)
    return template.render(context)
