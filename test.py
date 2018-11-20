#!/usr/bin/env python3

from flagship import *


def expect_fail(fn, arg_tuple):
    "Only works when function takes one argument, a tuple"

    try:
        fn(arg_tuple)
        assert False
    except (ValueError, IndexError):
        pass


def run_all():
    assert type_to_narg((int, int, int)) == dict(
        type_str="(int, int, int)", type=int, nargs=3
    )
    assert type_to_narg((int, int, ...)) == dict(
        type_str="(int, ...)", type=int, nargs="+"
    )
    assert type_to_narg([int]) == dict(type_str="[int]", type=int, nargs="*")

    assert type_to_narg(["a", "b", "c"]) == dict(
        type_str="{a,b,c}", choices=["a", "b", "c"]
    )

    expect_fail(type_to_narg, (1, int, ...))
    expect_fail(type_to_narg, (1, int))
    expect_fail(type_to_narg, (1))
    expect_fail(type_to_narg, ())

    expect_fail(type_to_narg, [int, int, int])
    # TODO maybe this should fail in a different way
    expect_fail(type_to_narg, [int, str, int])
    expect_fail(type_to_narg, [])

    # TODO
    # expect_fail(type_to_narg, (int, 1, ...))


if __name__ == "__main__":
    run_all()
