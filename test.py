#!/usr/bin/env python3
from flagship import *
import unittest
from unittest import mock


class TestDeriveFlags2(unittest.TestCase):
    def test_comprehensive(self):
        Suite = enum.Enum("Suite", "Hearts Spades Clubs Diamonds")
        mock_parser = mock.MagicMock()

        @derive_flags2(mock_parser)
        def main(
            p1: int,
            p2: typing.List[float],
            p3: typing.Tuple[int, int] = (3, 2),
            p4: (bool, "description") = True,
            p5: Suite = Suite.Diamonds,
        ):
            pass

        mock_parser.add_argument.assert_has_calls(
            [
                mock.call("p1", type=int, help=" (type: `int`)"),
                mock.call("p2", type=float, nargs="*", help=" (type: `List[float]`)"),
                mock.call(
                    "--p3",
                    type=int,
                    help=" (type: `Tuple[int, int]`) (default: `(3, 2)`)",
                    nargs=2,
                    default=(3, 2),
                    required=False,
                ),
                mock.call(
                    "--p4",
                    action="store_false",
                    default=True,
                    required=False,
                    help="description (action: `store_false`) (default: `True`)",
                ),
                mock.call(
                    "--p5",
                    choices=["Hearts", "Spades", "Clubs", "Diamonds"],
                    default=Suite.Diamonds,
                    help=" (default: `Suite.Diamonds`)",
                    required=False,
                ),
            ]
        )

    def test_init_objects_from_commandline(self):
        # Test classes to derive objects from
        class A:
            def __init__(self, x: (int, "ax desc"), y: typing.List[int]):
                self.x, self.y = x, y

        class B:
            def __init__(self, z: typing.Tuple[int, int, int], w: str):
                self.z, self.w = z, w

        mock_parser = mock.MagicMock()
        mock_parser.parse_args = mock.MagicMock(
            return_value=argparse.Namespace(x=0, y=[0], z=[0, 0, 0], w="foo")
        )

        # Test the parser got the expected arguments and the classes were initialized.
        a, b = init_objects_from_commandline(A, B, parser=mock_parser)

        mock_parser.add_argument.assert_has_calls(
            [
                mock.call("x", type=int, help="ax desc (type: `int`)"),
                mock.call("y", type=int, nargs="*", help=" (type: `List[int]`)"),
                mock.call(
                    "z", type=int, nargs=3, help=" (type: `Tuple[int, int, int]`)"
                ),
                mock.call("w", type=str, help=" (type: `str`)"),
            ]
        )
        mock_parser.parse_args.assert_called_once()

        self.assertEqual(a.x, 0)
        self.assertEqual(a.y, [0])
        self.assertEqual(b.z, [0, 0, 0])
        self.assertEqual(b.w, "foo")


class TestParseType(unittest.TestCase):
    def test_triple(self):
        self.assertEqual(
            parse_type((int, int, int)),
            dict(type_str="(int, int, int)", type=int, nargs=3),
        )

    def test_list(self):
        self.assertEqual(
            parse_type((int, int, ...)),
            dict(type_str="(int, ...)", type=int, nargs="+"),
        )

    def test_boolean_no_default(self):
        self.assertEqual(
            parse_type(bool), dict(action="store_true", action_str="store_true")
        )

    def test_boolean_default_false(self):
        self.assertEqual(
            parse_type(bool, False), dict(action="store_true", action_str="store_true")
        )

    def test_boolean_default_true(self):
        self.assertEqual(
            parse_type(bool, True), dict(action="store_false", action_str="store_false")
        )

    def test_sequence(self):
        self.assertEqual(
            parse_type((int, int, ...)),
            dict(type_str="(int, ...)", type=int, nargs="+"),
        )

    def test_fail_value_in_type(self):
        with self.assertRaises(ValueError):
            parse_type((1, int, ...))
        with self.assertRaises(ValueError):
            parse_type((1, int))
        with self.assertRaises(ValueError):
            parse_type((1))

    def test_fail_empty_tuple(self):
        with self.assertRaises(ValueError):
            parse_type(())

    def test_fail_bad_lists(self):
        with self.assertRaises(ValueError):
            parse_type([])
        with self.assertRaises(ValueError):
            parse_type([int, int, int])
        with self.assertRaises(ValueError):
            parse_type([int, str, int])


class TestSplitTypeAndDesc(unittest.TestCase):
    def test_type_and_desc(self):
        self.assertEqual(split_type_and_desc((int, "desc")), (int, "desc"))

    def test_tuple(self):
        self.assertEqual(split_type_and_desc((int, int)), ((int, int), ""))

    def test_fail_ty_ty_desc(self):
        with self.assertRaises(ValueError):
            split_type_and_desc((int, int, "desc"))


if __name__ == "__main__":
    unittest.main()
