from pathlib import Path
from typing import NamedTuple, List, Optional, Any, Union

import jinja2 as jinja2


class NameAndType(NamedTuple):
    name: str
    type: Optional[type]

    @property
    def mapped_type(self):
        return _convert_to_swift_type(self.type)


class Function(NamedTuple):
    name: str
    args: List[NameAndType]
    return_type: Optional[type] = None

    @property
    def mapped_return_type(self):
        return _convert_to_swift_type(self.return_type)


class SwiftObject(NamedTuple):
    object_name: str
    module: str
    static_vars: List[NameAndType]
    instance_vars: List[NameAndType]
    init_params: List[NameAndType]
    instance_methods: List[Function]
    static_methods: List[Function]

    @property
    def swift_object_name(self):
        return f'TPython{self.object_name}'

    @property
    def as_dict(self):
        return dict(swift_object_name=self.swift_object_name, **self._asdict())

    def render(self):
        return _render('object.swift.j2', self.as_dict)


def _convert_to_swift_type(python_type):
    if python_type == Any or python_type is None:
        return 'PythonObject'
    elif python_type.__class__ == type(Union) and python_type.__args__[1] == type(None):
        return _convert_to_swift_type(python_type.__args__[0]) + '?'
    return f'TPython{python_type.__name__.capitalize()}'


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


if __name__ == '__main__':
    obj = SwiftObject(
        object_name='BasicClass',
        module='basic',
        static_vars=[NameAndType(name='dimensions', type=int)],
        instance_vars=[NameAndType(name='x', type=None), NameAndType(name='y', type=None)],
        init_params=[NameAndType(name='x', type=float), NameAndType(name='y', type=float)],
        instance_methods=[Function(name='magnitude', args=[], return_type=float)],
        static_methods=[Function(name='a', args=[], return_type=Optional[int])],
    ).render()
    Path('/Users/biellls/Development/Swift/chip8/Sources/chip8/basic.swift').write_text(obj)
