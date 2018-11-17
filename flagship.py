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
    """Converts type annotation to arguments for arg parse.
    Examples:
        int        -> type=int, nargs=None
        (int, int) -> type=int, nargs=2
        (int, ...) -> type=int, nargs='+'
        [int]      -> type=int, nargs='*'
    """
    if isinstance(ty, type):
        return ty, None
    
    if isinstance(ty, tuple):
        # TODO (int, int, int, ...)
        if ty[-1] is Ellipsis and isinstance(ty[0], type):
            return ty[0], "+"
        # TODO (int, float, int)
        elif isinstance(ty[0], type):
            return ty[0], len(ty)
        else:
            raise ValueError("`{}` should be instance of type", ty[0])

    if isinstance(ty, list) and isinstance(ty[0], type):
        if len(ty) != 1:
            raise ValueError("Lists must have only one type inside")
        return ty[0], "*"

    raise ValueError("Case not handled:", ty)




def derive_flags_abusively(main):

    sig = inspect.signature(main)
    p = ArgumentParser(description=main.__doc__)
    main.__doc__ += "\nCommand Line Interface:"

    for param in sig.parameters.values():
        annotation = param.annotation if type(param.annotation) is dict else {}

        # Check for default and set name appropriately
        if param.default is not inspect._empty and "default" in annotation:
            raise ValueError("default value for `%s` defined twice!" % param.name)

        elif param.default is not inspect._empty:
            annotation["default"] = param.default

        # Arguments that have a default become optional flags
        name = "--" + param.name if "default" in annotation else param.name

        # Extend help description with boilerplate info
        annotation["help"] = annotation.get("help", "")
        if "type" in annotation:
            annotation["help"] += " (type:`%s`)" % annotation["type"].__name__

        if "action" in annotation:
            annotation["help"] += " (action: `%s`)" % annotation["action"]
        else:
            # If there is no action, then add a meta variable
            annotation["metavar"] = annotation.get("metavar", param.name[0])

        if "default" in annotation:
            annotation["help"] += " (default: `%s`)" % str(annotation["default"])

        p.add_argument(name, **annotation)
        main.__doc__ += "\n    {}: {}".format(param.name, annotation["help"])

    def new_main():
        flags = p.parse_args()
        main(**flags.__dict__)
    new_main.__name__ = main.__name__
    new_main.__doc__ = main.__doc__

    return new_main

@derive_flags_abusively
def main2(
    foo: int,
    bar: int = 11,
):
    """This is main.
    """
    for i, v in locals().items():
        print("`%s`:" % i, v)


if __name__ == "__main__":
    main2()
