"""Use Python introspection to derive command line flag interface with a decorator to main.

Author: casperneo@uchicago.edu
"""
from functools import wraps
import argparse
import typing
import enum
import inspect
import functools


def derive_flags(parser=None):
    def deriver(main):
        p = parser or argparse.ArgumentParser(description=main.__doc__)
        sig = inspect.signature(main)
        for param in sig.parameters.values():
            name, kwargs = get_flag_kwargs(param)
            p.add_argument(name, **kwargs)

        @wraps(main)
        def with_cli():
            flags = p.parse_args()
            main(**flags.__dict__)

        return with_cli

    return deriver


def get_flag_kwargs(param):
    """Returns command line flag argument derived from a function param signature.
    Args:
        param: `inspect.Parameter` instance. Number and type of cli arguments are derived
        from the annotation of this parameter. Flag names are the parameter names. Whether
        the flag is required or positional corresponds to the python parameter.
    Returns:
        name: flagname with "--" prepended if its an optional flag.
        kwargs: `argparse.ArgumentParser.add_argument` key word arguments.
    """
    kwargs = {}
    # Handle default values.
    if param.default is not inspect._empty:
        kwargs["default"] = param.default
        kwargs["required"] = param.default is None
        name = "--" + param.name
    else:
        name = param.name

    # Split type annotation if there is a description with it
    if type(param.annotation) is tuple and len(param.annotation) == 2:
        ty, kwargs["help"] = param.annotation

    elif isinstance(param.annotation, type):
        ty, kwargs["help"] = param.annotation, ""

    else:
        raise ValueError("Invalid annotation", param.name, param.annotation)

    # Default type to string when lacking annotation
    ty = str if ty is inspect._empty else ty

    # Add kwargs from type information and augment help description with action and type
    if isinstance(ty, typing.GenericMeta):
        kwargs["help"] += " (type: `" + str(ty).replace("typing.", "") + "`)"

        if ty.__origin__ is typing.Tuple:
            if any(a != ty.__args__[0] for a in ty.__args__):
                raise NotImplementedError("Heterogenous tuples not supported")
            kwargs["type"] = ty.__args__[0]
            kwargs["nargs"] = len(ty.__args__)

        elif ty.__origin__ is typing.List:
            kwargs["type"] = ty.__args__[0]
            kwargs["nargs"] = "*"

        else:
            raise ValueError("typing case not handled", ty)

    elif isinstance(ty, enum.EnumMeta):
        # convert ordered dict values to a list so equality can be compared in testing
        kwargs["choices"] = list(ty.__members__.values())
        # Default metavar will prepend Enum name to all variants, we only need variants.
        kwargs["metavar"] = "{" + ", ".join(ty.__members__) + "}"
        kwargs["type"] = ty.__getitem__
        kwargs["help"] += " (type: `%s`)" % ty.__name__

    elif ty is bool:
        kwargs["action"] = "store_false" if param.default is True else "store_true"
        kwargs["help"] += " (action: `%s`)" % kwargs["action"]

    else:
        kwargs["type"] = ty
        kwargs["help"] += " (type: `%s`)" % ty.__name__

    # Add default to help if it exists
    if "default" in kwargs:
        kwargs["help"] += " (default: `{}`)".format(kwargs["default"])

    return name, kwargs


def init_objects_from_commandline(*classes, description="", parser=None):
    """Given a list of classes, initialize them using commandline arguments.
    Args:
        *classes: various classes with flagship annotated `__init__`s
        description: description to prepend to all the class descriptions
        parser: ArgumentParser or mock object for testing.
    Returns:
        intances of `*classes`
    """
    desc = "Flags are used to initialize the following classes:"
    for c in classes:
        desc += "\n  %s:\t%s" % (c.__name__, c.__doc__ or "")

    p = parser or ArgumentParser(description=description + desc)

    inits = []
    for class_ in classes:
        obj_args = []
        sig = inspect.signature(class_.__init__)
        for param in sig.parameters.values():
            if param.name == "self":
                continue
            name, kwargs = get_flag_kwargs(param)
            p.add_argument(name, **kwargs)
            obj_args.append(name.replace("-", ""))
        inits.append(obj_args)

    flags = p.parse_args().__dict__

    objs = []
    for c, args in zip(classes, inits):
        args = {a: flags[a] for a in args}
        objs.append(c(**args))

    return objs


Suite = enum.Enum("Suite", "Hearts Spades Clubs Diamonds")


@derive_flags()
def main(
    p1: (int, "description for p1"),
    p2: typing.List[float],
    p3: Suite = Suite.Diamonds,
    p4: (typing.Tuple[int, int], "description for p4") = (3, 2),
    p5: (bool, "description for p5") = True,
):
    """This is main."""
    print("\n".join("{} = {}".format(*param) for param in sorted(locals().items())))


if __name__ == "__main__":
    main()
