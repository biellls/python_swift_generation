from typing import Tuple, List

from swift_python_wrapper.rendering import NameAndType, Function


def parse_overloads(source: str, indentation: int, module_or_class_name: str):
    overloads = [
        a_def(module_or_class_name, x.lstrip())
        for x in source.split('@overload\n')[1:]
        if x.startswith(('    ' * indentation) + 'def')
    ]
    return overloads


def get_tk(source: str, i):
    try:
        return source[i]
    except IndexError:
        return None


class ParseError(Exception):
    pass


WHITESPACE_TOKENS = [' ', '\t', '\n']


def a_whitespace(source: str, i: int, optional: bool = False) -> int:
    tk = get_tk(source, i)
    if not optional and tk not in WHITESPACE_TOKENS:
        raise ParseError(f'Expected whitespace, found {tk}')
    while tk in WHITESPACE_TOKENS:
        i += 1
        tk = get_tk(source, i)
    return i


def a_str(source: str, i: int, s: str) -> int:
    for c in s:
        tk = get_tk(source, i)
        if tk != c:
            raise ParseError(f'Attempting to parse "{s}". Expected "{c}", found "{tk}"')
        i += 1
    return i


def a_id(source: str, i: int) -> Tuple[str, int]:
    start = i
    tk = get_tk(source, i)
    if not tk.isalpha():
        raise ParseError(f'Char "{tk}" not allowed as first character in identifier')
    i += 1
    tk = get_tk(source, i)
    while tk == '_' or tk.isalnum():
        i += 1
        tk = get_tk(source, i)
    return source[start:i], i


def a_get_type(source: str, i: int) -> Tuple[type, int]:
    start = i
    identifier, i = a_id(source, i)

    if get_tk(source, i) == '[':
        i += 1
        i = a_whitespace(source, i, optional=True)
        t, i = a_get_type(source, i)
        i = a_whitespace(source, i, optional=True)
        while get_tk(source, i) == ',':
            i += 1
            i = a_whitespace(source, i, optional=True)
            t, i = a_get_type(source, i)
            i = a_whitespace(source, i, optional=True)
        tk = get_tk(source, i)
        if tk != ']':
            raise ParseError(f'Expected "]", found {tk}')
        i += 1
    return eval(source[start:i]), i


def a_typed_param(source: str, i: int) -> Tuple[NameAndType, int]:
    identifier, i = a_id(source, i)
    i = a_whitespace(source, i, optional=True)
    i = a_str(source, i, ':')
    i = a_whitespace(source, i, optional=True)
    t, i = a_get_type(source, i)
    i = a_whitespace(source, i, optional=True)
    return NameAndType(name=identifier, type=t), i


def a_typed_params(source: str, i: int) -> Tuple[List[NameAndType], int]:
    result = []
    tp, i = a_typed_param(source, i)
    result.append(tp)
    while get_tk(source, i) == ',':
        i += 1
        i = a_whitespace(source, i, optional=True)
        tp, i = a_typed_param(source, i)
        result.append(tp)
    return result, i


def a_def(class_name, source: str) -> Function:
    i = a_whitespace(source, 0, optional=True)
    i = a_str(source, i, 'def')
    i = a_whitespace(source, i)
    name, i = a_id(source, i)
    i = a_whitespace(source, i, optional=True)
    i = a_str(source, i, '(')
    i = a_whitespace(source, i, optional=True)
    name_types, i = a_typed_params(source, i)
    i = a_str(source, i, ')')
    i = a_whitespace(source, i, optional=True)
    if get_tk(source, i) == '-':
        i += 1
        tk = get_tk(source, i)
        if tk != '>':
            raise ParseError(f'Error while parsing -> found {tk}')
        i += 1
        i = a_whitespace(source, i, optional=True)
        return_type, i = a_get_type(source, i)
        i = a_whitespace(source, i, optional=True)
    else:
        return_type = None
    i = a_str(source, i, ':')
    i = a_whitespace(source, i, optional=True)
    i = a_str(source, i, '...')
    return Function(name=name, args=name_types, cls=class_name, return_type=return_type)
