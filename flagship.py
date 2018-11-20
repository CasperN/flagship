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

Author: casperneo@uchicago.edu
"""
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from typing import Tuple
import inspect
import functools


def type_to_narg(ty, default=None):
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
            return dict(action=action, action_str=action, required=required)

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

    raise ValueError("Case not handled:", ty)


def setup_argparse_kwargs(param, param_annotation=None):
    annotation = {}

    if param_annotation is None:
        param_annotation = param.annotation

    if param.default is not inspect._empty:
        annotation["default"] = param.default
        name = "--" + param.name
    else:
        name = param.name

    a = type_to_narg(param_annotation, default=annotation.get("default"))
    annotation.update(a)

    annotation["help"] = annotation.get("help", "")

    if "type_str" in annotation:
        annotation["help"] += " (type: `%s`)" % annotation.pop("type_str")

    if "action_str" in annotation:
        annotation["help"] += " (action: `%s`)" % annotation.pop("action_str")

    if "default" in annotation:
        annotation["help"] += " (default: `%s`)" % str(annotation["default"])

    return name, annotation


def derive_flags(main):

    sig = inspect.signature(main)
    p = ArgumentParser(description=main.__doc__)
    main.__doc__ += "\nCommand Line Interface:"

    for param in sig.parameters.values():

        if isinstance(param.annotation, type):
            name, annotation = setup_argparse_kwargs(param)
        else:
            assert isinstance(param.annotation, tuple)

            if len(param.annotation) == 2 and isinstance(param.annotation[1], str):
                name, annotation = setup_argparse_kwargs(
                    param, param_annotation=param.annotation[0]
                )
                # Prepend the description, since the message will already be partially constructed
                annotation["help"] = param.annotation[1] + annotation["help"]

            else:
                name, annotation = setup_argparse_kwargs(param)

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
    position_1: int,
    position_2: (float, "this is a description for `position_2`"),
    tuple: ((int, int), "This is a tuple") = (40, 40),
    sequence: ((int, ...), "(type, ...) means at least one instance of type") = 400,
    zero_or_more: ([float], "List of a type means zero or more instances of type") = 50,
    choice: (
        ["a", "b", "c", "d", "e"],
        "Use a list of strings as the type to specify a enum. "
        "Choose between these options.",
    ) = "a",
    boolean: (bool, "this is a bool") = True,
):
    """This is main. The commandline flags are derived from the argument annotations and
    the main docstring.
    """
    for i, v in locals().items():
        print("%s   \t=" % i, v)


if __name__ == "__main__":
    main()
