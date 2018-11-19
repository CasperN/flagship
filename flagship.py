"""Use Python introspection to derive command line flag interface with a decorator to main.

The goal of flagship, unlike `click` or `argparse`, is to strictly adhere to the Don't
Repeat Yourself (DRY) principle. We assume the flag arguments exactly the arguments to
your main function, and (ab)use python's type annotations to define the python type of
the command line inputs and also define the help description.

TODO:
    handle narg types with tuples
    better help message when type unspecified
    take docstring from module `main` is from rather than `main`'s function docstring

Author: casperneo@uchicago.edu
"""
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from typing import Tuple
import inspect
import functools


def type_to_narg(ty):
    """Converts type annotation to type string, instance, and nargs.
    Examples:
        int        -> "int", int, None
        (int, int) -> "(int, int)", int, 2
        (int, ...) -> "(int, ...)", int, '+'
        [int]      -> "[int]", int, '*'
    """
    if isinstance(ty, type):
        return ty.__name__, ty, None

    if isinstance(ty, tuple):

        if any(t != ty[0] for t in ty[:-1]) or (ty[0] != ty[-1] and ty[-1] is not ...):
            raise ValueError("Heterogenous tuples not supported", ty)

        # Sequence type
        if ty[-1] is Ellipsis and isinstance(ty[0], type):
            return f"({ ty[0].__name__ }, ...)", ty[0], "+"

        # Tuple Type
        elif isinstance(ty[0], type):
            type_str = "(" + ", ".join(i.__name__ for i in ty) + ")"
            return type_str, ty[0], len(ty)

        else:
            raise ValueError("`{}` should be instance of type".format(ty[0]))

    # List Type
    if isinstance(ty, list) and isinstance(ty[0], type):
        if len(ty) != 1:
            raise ValueError("Lists must have exactly one type inside")
        return f"[{ ty[0].__name__ }]", ty[0], "*"

    # Enum (choices) type
    if isinstance(ty, list) and all(isinstance(t, str) for t in ty):
        raise NotImplementedError("Enums")

    raise ValueError("Case not handled:", ty)


def setup_no_description(param, param_annotation=None):
    annotation = {}

    if param_annotation is None:
        param_annotation = param.annotation

    if param.default is not inspect._empty:
        annotation["default"] = param.default
        name = "--" + param.name
    else:
        name = param.name

    type_str, annotation["type"], annotation["nargs"] = type_to_narg(param_annotation)
    # We'll end up printing the wrong type. This is the tradeoff of using values
    # to express types instead of the native types.
    annotation["help"] = " (type:`%s`)" % type_str

    if "default" in annotation:
        annotation["help"] += " (default: `%s`)" % str(annotation["default"])

    return name, annotation


def derive_flags(main):

    sig = inspect.signature(main)
    p = ArgumentParser(description=main.__doc__)
    main.__doc__ += "\nCommand Line Interface:"

    for param in sig.parameters.values():

        if isinstance(param.annotation, type):
            name, annotation = setup_no_description(param)
        else:
            assert isinstance(param.annotation, tuple)

            if len(param.annotation) == 2 and isinstance(param.annotation[1], str):
                name, annotation = setup_no_description(
                    param, param_annotation=param.annotation[0]
                )
                # Prepend the description, since the message will already be partially constructed
                annotation["help"] = param.annotation[1] + annotation["help"]

            else:
                name, annotation = setup_no_description(param)

        p.add_argument(name, **annotation)
        main.__doc__ += "\n    {}: {}".format(param.name, annotation["help"])

    def new_main():
        flags = p.parse_args()
        main(**flags.__dict__)

    new_main.__name__ = main.__name__
    new_main.__doc__ = main.__doc__

    return new_main


@derive_flags
def main(
    foo: int,
    bar: ((int, int), "This is a tuple") = (40, 40),
    baz: (int, ...) = 400,
    bun: ([int], "descriptorzzzzz") = 50,
    # choice: ("a b c d e".split(" "), "Choose between these options.") = "a",
):
    """This is main.
    """
    for i, v in locals().items():
        print("`%s`:" % i, v)


if __name__ == "__main__":
    main()
