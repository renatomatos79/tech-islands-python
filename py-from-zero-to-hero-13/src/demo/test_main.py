import unittest
from main import calc

class TestCalc(unittest.TestCase):

    def test_calc_with_positive_numbers(self):
        self.assertEqual(calc(2, 3), 6)

    def test_calc_with_negative_numbers(self):
        self.assertEqual(calc(-2, 3), -6)

    def test_calc_with_zero(self):
        self.assertEqual(calc(0, 5), 0)

if __name__ == '__main__':
    unittest.main()