import unittest
import numpy as np
from mkmqr.binary import *


t = True
f = False


class TestMatrix(unittest.TestCase):
    def test_bin2mat(self):
        binaries = np.array([
            0b1100,
            0b1010
        ])
        excepted = np.array([
            [t, t, f, f],
            [t, f, t, f]
        ])
        actual = bin2mat(binaries, 4)
        self.assertTrue((excepted == actual).all())

    def test_bin2mat_negative(self):
        binaries = np.array([
            0b1100,
            -1
        ])
        with self.assertRaises(ValueError):
            bin2mat(binaries, 4)

    def test_bin2mat_overflow(self):
        binaries = np.array([
            0b01100,
            0b11100
        ])
        with self.assertRaises(ValueError):
            bin2mat(binaries, 4)

    def test_mat2str(self):
        binaries = np.array([
            [t, t, f, f],
            [t, f, t, f]
        ])
        excepted = '1100\n1010'
        actual = mat2str(binaries, on='1', off='0')
        self.assertEqual(excepted, actual)

    def test_merge_matrix(self):
        mat1 = np.array([[t, t, f, f]])
        mat2 = np.array([[t, f, t, f]])
        excepted = np.array([[f, t, t, f]])
        actual = merge_matrix([mat1, mat2])
        self.assertTrue((excepted == actual).all())

    def test_empty_matrix(self):
        excepted = np.zeros((2, 2))
        actual = empty_matrix(2)
        self.assertTrue((excepted == actual).all())

    def test_empty_matrix_0(self):
        excepted = np.zeros([0, 0])
        actual = empty_matrix(0)
        self.assertTrue((excepted == actual).all())

    def test_empty_matrix_rect(self):
        excepted = np.zeros((2, 3))
        actual = empty_matrix((2, 3))
        self.assertTrue((excepted == actual).all())

    def test_empty_matrix_negative(self):
        with self.assertRaises(ValueError):
            empty_matrix(-1)


if __name__ == '__main__':
    unittest.main()
