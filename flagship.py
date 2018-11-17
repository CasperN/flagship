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
        return ty.__name__, ty, None

    if isinstance(ty, tuple):
        # TODO (int, int, int, ...)
        if ty[-1] is Ellipsis and isinstance(ty[0], type):
            return "({}, ...)".format(ty[0].__name__), ty[0], "+"
        # TODO (int, float, int)
        elif isinstance(ty[0], type):
            type_str = "("
            for i in ty[:-1]:
                type_str += "{}, ".format(i.__name__)
            type_str += "{})".format(ty[-1].__name__)

            return type_str, ty[0], len(ty)
        else:
            raise ValueError("`{}` should be instance of type".format(ty[0]))

    if isinstance(ty, list) and isinstance(ty[0], type):
        if len(ty) != 1:
            raise ValueError("Lists must have only one type inside")
        return "[{}]".format(ty[0].__name__), ty[0], "*"

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

def setup_with_description(param):
    assert len(param.annotation) == 2
    assert isinstance(param.annotation[1], str)

    name, annotation = setup_no_description(param, param_annotation=param.annotation[0])

    # Prepend the description, since the message will already be partially constructed
    annotation["help"] = param.annotation[1] + annotation["help"]

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

            # hmm... not very flexible
            if isinstance(param.annotation[1], str):
                name, annotation = setup_with_description(param)
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
    bar: ((int, int), "wow such description") = 40,
    baz: ((int, ...), "wow cool") = 400,
):
    """This is main.
    """
    for i, v in locals().items():
        print("`%s`:" % i, v)


if __name__ == "__main__":
    main()
