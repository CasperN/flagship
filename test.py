#!/usr/bin/env python3

from flagship import *


def expect_fail(fn, arg_tuple):
    "Only works when function takes one argument, a tuple"

    try:
        fn(arg_tuple)
        assert False
    except (ValueError, IndexError):
        pass

def test():
    assert type_to_narg((int, int, int)) == (int, 3)
    assert type_to_narg((int, int, ...)) == (int, "+")

    expect_fail(type_to_narg, (1, int, ...))
    expect_fail(type_to_narg, (1, int))
    expect_fail(type_to_narg, (1))
    expect_fail(type_to_narg, ())

    assert type_to_narg([int]) == (int, "*")
    expect_fail(type_to_narg, [int, int, int])
    expect_fail(type_to_narg, [])
    # TODO figure this out
    # assert type_to_narg([int, str, int]) == (int, "*")

    # TODO
    # expect_fail(type_to_narg, (int, 1, ...))

if __name__ == "__main__":
    test()
