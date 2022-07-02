import unittest
from micro_qr.error_correction import PolynomialRing, ReedSolomonCode


class TestReedSolomonCode(unittest.TestCase):
    primitive_polynomial = PolynomialRing(0b1_0001_1101)
    
    @staticmethod
    def from_list(*cof):
        return [PolynomialRing(c) for c in cof]

    def test_2d(self):
        generator_polynomial = self.from_list(1, 3, 2)
        rs_code = ReedSolomonCode(self.primitive_polynomial, generator_polynomial)

        table = [
            ([163, 218, 208], [110, 199]),
            ([46, 0, 0], [167, 137])
        ]

        for q, excepted in table:
            excepted = self.from_list(*excepted)
            actual = rs_code.encode(self.from_list(*q))
            with self.subTest():
                for _e, _a in zip(excepted, actual):
                    self.assertEqual(_e._coefficient, _a._coefficient)

    def test_5d(self):
        generator_polynomial = self.from_list(1, 31, 198, 63, 147, 116)
        rs_code = ReedSolomonCode(self.primitive_polynomial, generator_polynomial)

        table = [
            ([233, 253, 6, 34, 80], [252, 3, 233, 41, 95]),
        ]

        for q, excepted in table:
            excepted = self.from_list(*excepted)
            actual = rs_code.encode(self.from_list(*q))
            with self.subTest():
                for _e, _a in zip(excepted, actual):
                    self.assertEqual(_e._coefficient, _a._coefficient)


if __name__ == '__main__':
    unittest.main()
