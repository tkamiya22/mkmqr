import unittest
import numpy as np
from mkmqr.binary import *


t = True
f = False


class TestArray(unittest.TestCase):
    def test_arr2bin(self):
        arr = np.array([t, f, t, f])
        excepted = 0b1010
        actual = arr2bin(arr)
        self.assertEqual(excepted, actual)

    def test_bin2arr(self):
        binary = 0b1010
        excepted = np.array([t, f, t, f])
        actual = bin2arr(binary, 4)
        self.assertTrue((excepted == actual).all())

    def test_bin2arr_highest_is_0(self):
        binary = 0b0101
        excepted = np.array([f, t, f, t])
        actual = bin2arr(binary, 4)
        self.assertTrue((excepted == actual).all())

    def test_bin2arr_negative(self):
        with self.assertRaises(ValueError):
            bin2arr(-1, 4)

    def test_bin2arr_overflow(self):
        binary = 0b10000
        with self.assertRaises(ValueError):
            bin2arr(binary, 4)

    def test_arr2str(self):
        arr = np.array([t, f, t, f])
        excepted = '1010'
        actual = arr2str(arr)
        self.assertEqual(excepted, actual)

    def test_arr2str_sep(self):
        arr = np.array([t] * 8 + [f] * 8)
        excepted = '11111111 00000000'
        actual = arr2str(arr, byte_sep=' ')
        self.assertEqual(excepted, actual)

    def test_concat_arr(self):
        arr1 = np.array([t, f, f, f])
        arr2 = np.array([t, f, f, t])
        excepted = np.array([t, f, f, f, t, f, f, t])
        actual = concat_arr([arr1, arr2])
        self.assertTrue((excepted == actual).all())


if __name__ == '__main__':
    unittest.main()
