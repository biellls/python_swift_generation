# Swift Python Wrapper

Status: Alpha.

Generates Swift wrapper files for typed Python 3 code or stub files. Improves Python interop by allowing auto-complete, type safety and null safety at the boundary. Removes unintuitive bugs that could happen from using the Python module such as:

```Swift
let itertools = Python.import("itertools")
itertools.count(1)  // Calls swift sequence count, not itertools one
```

```Swift
let itertools = TPython.import.itertools
itertools.count(1) // Calls itertools count since it knows itertools is a module not a sequence and doesn't have a built in count
```

### Finished

- Generate wrappers for functions, classes and modules
- Translate python types to swift
- Optional types map to swift nullable (null safe Python!)
- Union types generate overloaded function definitions
- @overload annotations are parsed from the source file manually (afaik there's no other way) and generate overloaded function definitions
- If no return type is specified it returns a discardable PythonObject
- Support python properties
- Support static methods and class methods
- Maps magic methods to swift special functions

### Pending
- Improve public/private visibility
- Improve default values handling
- Positional only arguments (C functions)
- Handle init overloads (works for regular functions/methods already)
- Handle -> None annotation in init
- Handle nested unions
- Handle slices
- Add safety checks in inits to make sure they don't wrap the incorrect python object?
- Generics
- Add sequence support
- Handle protocols (how? Manually define conformance externally?)
- Add error throws annotations (annotating python stubs/code)
- Handle args and kwargs
- Add docstrings
- Nested modules
- Add context managers
