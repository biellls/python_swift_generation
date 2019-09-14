import inspect
from pathlib import Path
from typing import NamedTuple, List, Optional, Any, Union, _ForwardRef, Tuple, Sequence

import jinja2 as jinja2


class NameAndType(NamedTuple):
    name: str
    type: Optional[type]
    default_value: Any = inspect.Parameter.empty

    @property
    def mapped_type(self):
        return _convert_to_swift_type(self.type)

    @property
    def has_default_value(self):
        return self.default_value != inspect.Parameter.empty


class Function(NamedTuple):
    name: str
    args: List[NameAndType]
    cls: str
    return_type: Optional[type] = None

    @property
    def mapped_return_type(self):
        return _convert_to_swift_type(self.return_type)

    @property
    def static_method(self):
        return self.cls == 'staticmethod'

    @property
    def instance_method(self):
        return self.cls == 'instancemethod'

    @property
    def module_function(self):
        return self.cls == 'modulefunction'


class SwiftClass(NamedTuple):
    object_name: str
    module: str
    static_vars: List[NameAndType]
    instance_vars: List[NameAndType]
    init_params: List[NameAndType]
    methods: List[Function]
    magic_methods: 'MagicMethods'

    @property
    def swift_object_name(self):
        return f'TPython{self.object_name}'

    @property
    def as_dict(self):
        return dict(swift_object_name=self.swift_object_name, **self._asdict())

    def render_magic_methods(self):
        return _render('magic_methods.swift.j2', self.as_dict)

    def render(self):
        return _render('object.swift.j2', dict(rendered_magic_methods=self.render_magic_methods(), **self.as_dict))


class SwiftModule(NamedTuple):
    module_name: str
    vars: List[NameAndType]
    functions: List[Function]
    classes: List[SwiftClass]

    @property
    def swift_module_name(self):
        return f'TPython{self.module_name.replace(".", "_")}'

    @property
    def as_dict(self):
        return dict(swift_class_name=self.swift_module_name, **self._asdict())

    def render(self):
        return _render('module.swift.j2', self.as_dict)


def _convert_to_swift_type(python_type) -> str:
    def capitalize(s):
        return s[:1].upper() + s[1:]
    if python_type == Any or python_type is None:
        return 'PythonObject'
    elif isinstance(python_type, str):
        return f'TPython{capitalize(python_type)}'
    elif python_type.__class__ == type(Union) and python_type.__args__[1] == type(None):
        return _convert_to_swift_type(python_type.__args__[0]) + '?'
    elif python_type.__class__ == type(List):
        return f'TPythonList<{_convert_to_swift_type(python_type.__args__[0])}>'
    elif python_type.__class__ == type(Sequence):
        return f'TPythonSequence<{_convert_to_swift_type(python_type.__args__[0])}>'
    elif isinstance(python_type, _ForwardRef):
        return f'TPython{capitalize(python_type.__forward_arg__)}'
    return f'TPython{capitalize(python_type.__name__)}'


class BinaryMagicMethod(NamedTuple):
    symbol: str
    python_magic_method: str
    swift_protocol_name: Optional[str]
    right_classes: List[Tuple[type, type]]  # List of right hand side types and return types for each


class UnaryMagicMethod(NamedTuple):
    symbol: str
    python_magic_method: str
    swift_protocol_name: Optional[str]


class MagicMethods(NamedTuple):
    # Equality
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
    div__: Union[bool, BinaryMagicMethod] = False
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
