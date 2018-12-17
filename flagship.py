"""Use Python introspection to derive command line flag interface with a decorator to main.

The goal of flagship, unlike `click` or `argparse`, is to strictly adhere to the Don't
Repeat Yourself (DRY) principle. We assume the flag arguments exactly the arguments to
your main function, and (ab)use python's type annotations to define the python type of
the command line inputs and also define the help description.

TODO:
    metavar
    booleans
    better help message when type unspecified
    `derive_flags` should take arguments e.g. docstring
    Decorator that initializes multiple classes in main
    Unit tests instead of examples in docstrings.

Author: casperneo@uchicago.edu
"""
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, RawTextHelpFormatter
from typing import Tuple
import inspect
import functools


def parse_type(ty, default=None):
    """Converts type annotation to type string, instance, and nargs.
    Examples:
        int        -> "int", int, None
        (int, int) -> "(int, int)", int, 2
        (int, ...) -> "(int, ...)", int, '+'
        [int]      -> "[int]", int, '*'
    """
    if isinstance(ty, type):
        # Normal type case
        if ty is not bool:
            return dict(type_str=ty.__name__, type=ty)

        # Boolean flag case
        elif ty is bool:
            action = "store_false" if default is True else "store_true"
            required = default is None
            return dict(action=action, action_str=action)

    if isinstance(ty, tuple):
        if not isinstance(ty[0], type):
            raise ValueError("`{}` should be instance of type".format(ty[0]))

        if any(t != ty[0] for t in ty[:-1]) or (ty[0] != ty[-1] and ty[-1] is not ...):
            raise ValueError("Heterogenous tuples not supported", ty)

        # Sequence type
        if ty[-1] is Ellipsis and isinstance(ty[0], type):
            return dict(type_str=f"({ ty[0].__name__ }, ...)", type=ty[0], nargs="+")

        # Tuple Type
        else:
            type_str = "(" + ", ".join(i.__name__ for i in ty) + ")"
            return dict(type_str=type_str, type=ty[0], nargs=len(ty))

    # List Type
    if isinstance(ty, list) and isinstance(ty[0], type):
        if len(ty) != 1:
            raise ValueError("Lists must have exactly one type inside")
        return dict(type_str=f"[{ ty[0].__name__ }]", type=ty[0], nargs="*")

    # Enum (choices) type
    if isinstance(ty, list) and all(isinstance(t, str) for t in ty):
        # NOTE: argparse displays choices themselves so no need to specify type_str
        return {"choices": ty}

    raise ValueError("Type case not handled:", ty)


def _split_type_and_desc(annotation):
    """Seperates flagship types from descriptions and raises ValueError if parsing fails.
    Examples:
        (int, "desc")       => int, "desc"
        (int, int)          => (int, int), ""
        (int, int, "desc")  => ValueError
    """
    # Case `arg: <type>` or `arg: (<type>, ..., <type>)`
    if (
        isinstance(annotation, type)
        or isinstance(annotation, tuple)
        and all(isinstance(a, type) for a in annotation)
    ):
        return annotation, ""

    # Case `arg: (<type>, "description")`
    elif (
        isinstance(annotation, tuple)
        and len(annotation) == 2
        and isinstance(annotation[1], str)
    ):
        return annotation

    else:
        raise ValueError("Annotation case not handled", annotation)


def make_argparse_argument_kwargs(param):
    """Converts signature.param into a dictonary kwargs for ArgumentParser.add_argument()
    """
    kwargs = {}
    # Parse Type and description from annotation
    type_, kwargs["help"] = _split_type_and_desc(param.annotation)

    # Handle default values.
    if param.default is not inspect._empty:
        kwargs["default"] = param.default
        kwargs["required"] = param.default is None
        name = "--" + param.name
    else:
        name = param.name

    a = parse_type(type_, default=kwargs.get("default"))
    kwargs.update(a)

    # Augment help string.
    if "type_str" in kwargs:
        kwargs["help"] += " (type: `%s`)" % kwargs.pop("type_str")

    if "action_str" in kwargs:
        kwargs["help"] += " (action: `%s`)" % kwargs.pop("action_str")

    if "default" in kwargs:
        kwargs["help"] += " (default: `%s`)" % str(kwargs["default"])

    return name, kwargs


def derive_flags(main):
    """Create a flag interface for a "main" function.

    The flags are derived from the arguments and type annotations. Example arguments:
        `foo` ~ positional cli argument that takes a string
        `foo: int` ~ positional cli argument that takes an integer
        `foo: (int, "is a foo")` ~ positional cli argument that take an integer with help
            description "is a foo"
        `foo: (int, "is a foo") = 0` ~ optional flag `--foo` that take an integer, has
            description "is a foo" and has default value 0.
    """
    sig = inspect.signature(main)

    p = ArgumentParser(description=main.__doc__)
    main.__doc__ += "\nCommand Line Interface:"

    for param in sig.parameters.values():
        name, kwargs = make_argparse_argument_kwargs(param)

        p.add_argument(name, **kwargs)
        main.__doc__ += "\n    {}: {}".format(name, kwargs["help"])

    def new_main():
        flags = p.parse_args()
        main(**flags.__dict__)

    new_main.__name__ = main.__name__
    new_main.__doc__ = main.__doc__

    return new_main


def init_objects_from_commandline(*classes, description=""):
    """Given a list of classes, initialize them using commandline arguments."""

    foo = "Flags are used to initialize the following classes:"
    for c in classes:
        foo += "\n  %s:\t%s" % (c.__name__, c.__doc__ or "")

    p = ArgumentParser(
        description=description + foo, formatter_class=RawTextHelpFormatter
    )
    inits = []
    for class_ in classes:
        obj_args = []
        sig = inspect.signature(class_.__init__)
        for param in sig.parameters.values():
            if param.name == "self":
                continue
            name, kwargs = make_argparse_argument_kwargs(param)
            p.add_argument(name, **kwargs)
            obj_args.append(name.replace("-", ""))
        inits.append(obj_args)

    flags = p.parse_args().__dict__

    return [c(**{a: flags[a] for a in args}) for c, args in zip(classes, inits)]


def test_cls():
    class A:
        "A is a test class"

        def __init__(self, x: (int, "X"), y: (float, "why")):
            self.x, self.y = x, y
        def __str__(self):
            return "A ( x:{}, y:{} )".format(self.x, self.y)

    class B:
        "B is a test class too"

        def __init__(self, w: ((int, int)), z: (int, "zzz") = 4):
            self.w, self.z = w, z
        def __str__(self):
            return "B ( w:{}, z:{} )".format(self.w, self.z)


    a, b = init_objects_from_commandline(A, B)
    print(a, b)


@derive_flags
def main(
    position_1: int,
    position_2: (float, "this is a description for `position_2`"),
    tuple: ((int, int), "This is a tuple") = (40, 40),
    sequence: ((int, ...), "(type, ...) means at least one instance of type") = 400,
    zero_or_more: ([float], "List of a type means >= 0 instances of type") = [0],
    choice: (
        ["a", "b", "c", "d", "e"],
        "Use a list of strings as the type to specify a enum. "
        "Choose between these options.",
    ) = "a",
    boolean: (
        bool,
        "This is a bool. The flag is required if the default argument is None.",
    ) = True,
):
    """This is main. The commandline flags are derived from the argument annotations and
    the main docstring.
    """
    for i, v in locals().items():
        print("%s   \t=" % i, v)


if __name__ == "__main__":
    main()
    # test_cls()
