from distutils.core import setup

setup(
    name='swift-python-wrapper',
    version='0.1',
    description='Generates swift code to wrap typed python',
    author='Gabriel Llobera',
    packages=['swift_python_wrapper'],
    install_requires=['click', 'jinja2'],
    entry_points={
        'console_scripts': [
            'swrap=swift_python_wrapper.cli:cli',
        ]
    },
    license='MIT License',
)
