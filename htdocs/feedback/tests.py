from django.test import TestCase
from .utils import smart_list

class SmartListTests(TestCase):

    def test_smart_list_empty(self):
        "Test the smart_list function with empty input."
        self.assertEqual(smart_list(""), [])
        self.assertEqual(smart_list(" "), [])
        self.assertEqual(smart_list("  "), [])
        self.assertEqual(smart_list("[]"), [])
        self.assertEqual(smart_list(u"[]"), [])
        self.assertEqual(smart_list(u"[  ]"), [])
        self.assertEqual(smart_list("[   ]"), [])
        self.assertEqual(smart_list("[21]"), ["21"])
        self.assertEqual(smart_list(None), [])

    def test_smart_list_single_values(self):
        "Test the smart_list function with valid single value input."
        self.assertEqual(smart_list("1"), ["1"])
        self.assertEqual(smart_list(u"ß "), [u"ß"])
        self.assertEqual(smart_list(1), [1])
        self.assertEqual(smart_list((1,)), [1])
        self.assertEqual(smart_list([1]), [1])

    def test_smart_list_errors(self):
        "Test the smart_list function raises expected ValueErrors."
        self.assertRaises(ValueError, smart_list, {"1": None})
        self.assertRaises(ValueError, smart_list, object())

    def test_smart_list_delimiter(self):
        "Test the smart_list delimiter works."
        self.assertEqual(smart_list("1,2"), ["1", "2"])
        self.assertEqual(smart_list("1 2"), ["1 2"])
        self.assertEqual(smart_list("1 2", " "), ["1", "2"])

    def test_smart_list_func(self):
        "Test the smart_list func parameter works."
        self.assertEqual(smart_list("1,2", func=lambda x: int(x)), [1, 2])
        self.assertEqual(smart_list("1,2", func=lambda x: int(x) * 2), [2, 4])
        self.assertEqual(smart_list("[21]", func=lambda x: int(x)), [21])
        self.assertRaises(
            ValueError,
            smart_list,
            "1,A",
            func=lambda x: int(x) * 2
        )