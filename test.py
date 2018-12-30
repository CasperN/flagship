#!/usr/bin/env python3
from flagship import *
import unittest
from unittest import mock


class TestDeriveFlags(unittest.TestCase):
    def test_comprehensive(self):
        Suite = enum.Enum("Suite", "Hearts Spades Clubs Diamonds")
        mock_parser = mock.MagicMock()

        @derive_flags(mock_parser)
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


if __name__ == "__main__":
    unittest.main()
