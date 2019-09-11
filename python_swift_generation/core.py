from importlib import util


class BrokenImportError(Exception):
    pass


def load_module_from_path(module_path):
    spec = util.spec_from_file_location("module.name", module_path)
    module = util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except (NameError, SyntaxError):
        raise BrokenImportError(f'Error loading module {module_path}')
    return module
