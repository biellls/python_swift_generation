from pathlib import Path
from typing import NamedTuple, List, Optional

import jinja2 as jinja2


class NameAndType(NamedTuple):
    name: str
    type: Optional[str]


class Function(NamedTuple):
    name: str
    args: List[NameAndType]
    return_type: Optional[str] = None


class SwiftObject(NamedTuple):
    object_name: str
    module: str
    static_vars: List[NameAndType]
    instance_vars: List[NameAndType]
    init_params: List[NameAndType]
    instance_methods: List[Function]

    @property
    def swift_object_name(self):
        return f'TPython{self.object_name}'

    @property
    def as_dict(self):
        return dict(swift_object_name=self.swift_object_name, **self._asdict())

    def render(self):
        return _render('object.swift.j2', self.as_dict)


def _convert_to_swift_type(python_type: str):
    return f'TPython{python_type.capitalize()}'


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
        static_vars=[NameAndType(name='dimensions', type='int')],
        instance_vars=[NameAndType(name='x', type='float'), NameAndType(name='y', type='float')],
        init_params=[NameAndType(name='x', type='float'), NameAndType(name='y', type='float')],
        instance_methods=[Function(name='magnitude', args=[], return_type='float')]
    ).render()
    Path('/Users/biellls/Development/Swift/chip8/Sources/chip8/basic.swift').write_text(obj)
