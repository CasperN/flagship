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


def derive_flags(main, print_args=False):
    sig = inspect.signature(main)
    p = ArgumentParser(description=main.__doc__)

    for param in sig.parameters.values():
        description = ""

        # Turn kwargs into optional flags
        if param.default is inspect._empty:
            name = param.name
            default = None
        else:
            name = "--" + param.name
            default = param.default

        # Add type annotations
        ty = None if param.annotation is inspect._empty else param.annotation
        if ty is not bool:
            description += "(type: `{}`) ".format(param.annotation.__name__)

        # Handle Booleans
        if ty is bool and default:
            action = "store_false"
        elif ty is bool:
            action = "store_true"
        else:
            action = None

        description += "" if action is None else "(%s)" % action.replace("_", "s ")

        # Add argument
        if action is not None:
            p.add_argument(name, action=action, help=description)

        else:
            p.add_argument(name, type=ty, default=default, help=description)

    @functools.wraps(main)
    def new_main():
        flags = p.parse_args()

        if print_args:
            print_flag_dict(flags.__dict__)

        main(**flags.__dict__)

    return new_main


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
        if ty[-1] is Ellipsis and isinstance(ty[0], type):
            return ty[0], "+"
        elif isinstance(ty[0], type):
            return ty[0], len(ty)
        else:
            raise ValueError("`{}` should be instance of type", ty[0])

    if isinstance(ty, list) and isinstance(ty[0], type):
        return ty[0], "*"

    raise ValueError("Case not handled:", ty)




@derive_flags
def main(foo: Tuple[float, float], bar: float = 3.14, baz: bool = False):
    """This is the docstring for main. when the `@derive_flags` decorator is added,
    it becomes the description for the whole file.
    """
    print(foo, bar, baz)


def derive_flags_abusively(main):

    sig = inspect.signature(main)
    p = ArgumentParser(description=main.__doc__)
    main.__doc__ += "\nCommand Line Interface:"

    for param in sig.parameters.values():
        kwargs = param.annotation if type(param.annotation) is dict else {}

        # Check for default and set name appropriately
        if param.default is not inspect._empty and "default" in kwargs:
            raise ValueError("default value for `%s` defined twice!" % param.name)

        elif param.default is not inspect._empty:
            kwargs["default"] = param.default

        name = "--" + param.name if "default" in kwargs else param.name

        # Extend help description with boilerplate info
        kwargs["help"] = kwargs.get("help", "")
        if "type" in kwargs:
            kwargs["help"] += " (type:`%s`)" % kwargs["type"].__name__

        if "action" in kwargs:
            kwargs["help"] += " (action: `%s`)" % kwargs["action"]
        else:
            # If there is no action, then add a meta variable
            kwargs["metavar"] = kwargs.get("metavar", param.name[0])

        if "default" in kwargs:
            kwargs["help"] += " (default: `%s`)" % str(kwargs["default"])

        p.add_argument(name, **kwargs)
        main.__doc__ += "\n    {}: {}".format(param.name, kwargs["help"])


    #@functools.wraps(main)
    def new_main():
        flags = p.parse_args()
        main(**flags.__dict__)
    new_main.__name__ = main.__name__
    new_main.__doc__ = main.__doc__

    return new_main

def test(
    foo: ((int, int), "this should expect a tuple of two integers"),
    bar: ([float], "this should expect a list of floats which may be empty") = [],

):
    pass





@derive_flags_abusively
def main2(
    foo: dict(type=float, help="Well this is a thing..."),
    bar: dict(
        type=int,
        help="This may be the concise way I can define flags and stuff for a program "
        "without having to write some kind of parser.",
        default=11,
    ),
    baz: dict(
        type=int, # type=(int, int)
        nargs=2,
        help="Man, python introspection is kind of ridiculous. Why is it even possible "
        "for me to do this? This is witchcraft!",
    ) = (128, 142),
    gaf: dict(action="store_true") = False,
):
    """This is main.
    """
    for i, v in locals().items():
        print("`%s`:" % i, v)


if __name__ == "__main__":
    main2()
