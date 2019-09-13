import click

from swift_python_wrapper.core import build_swift_wrappers_module


@click.group()
def cli():
    """Swift generation CLI"""
    pass


@cli.command()
@click.option('--module-path', required=True)
@click.option('--target-dir', required=True)
@click.option('--module-name', default=None)
def generate(module_name, module_path, target_dir):
    """Build Swift wrappers for python module"""
    build_swift_wrappers_module(module_name, module_path, target_dir)
