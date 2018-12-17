#!/usr/bin/env python3
from flagship import *
import unittest


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
