import inspect
from pathlib import Path
from typing import NamedTuple, List, Optional, Any, Union, _ForwardRef

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

    @property
    def swift_object_name(self):
        return f'TPython{self.object_name}'

    @property
    def as_dict(self):
        return dict(swift_object_name=self.swift_object_name, **self._asdict())

    def render(self):
        return _render('object.swift.j2', self.as_dict)


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
    elif isinstance(python_type, _ForwardRef):
        return f'TPython{capitalize(python_type.__forward_arg__)}'
    return f'TPython{capitalize(python_type.__name__)}'


def _render(template_name: str, context: dict):
    search_path = Path(__file__).parent / 'templates'
    template_loader = jinja2.FileSystemLoader(searchpath=str(search_path))
    template_env = jinja2.Environment(loader=template_loader)

    template_env.trim_blocks = True
    template_env.lstrip_blocks = True
    template_env.keep_trailing_newline = True

    template_env.filters.update(convert_to_swift_type=_convert_to_swift_type)

    dag_template = template_env.get_template(template_name)
    return dag_template.render(context)
