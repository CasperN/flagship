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
    assert parse_type((int, int, int)) == dict(
        type_str="(int, int, int)", type=int, nargs=3
    )
    assert parse_type((int, int, ...)) == dict(
        type_str="(int, ...)", type=int, nargs="+"
    )
    assert parse_type([int]) == dict(type_str="[int]", type=int, nargs="*")

    assert parse_type(["a", "b", "c"]) == {"choices": ["a", "b", "c"]}

    expect_fail(parse_type, (1, int, ...))
    expect_fail(parse_type, (1, int))
    expect_fail(parse_type, (1))
    expect_fail(parse_type, ())

    expect_fail(parse_type, [int, int, int])
    # TODO maybe this should fail in a different way
    expect_fail(parse_type, [int, str, int])
    expect_fail(parse_type, [])

    # TODO
    # expect_fail(parse_type, (int, 1, ...))


if __name__ == "__main__":
    run_all()
