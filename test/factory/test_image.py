"""
デコーダーは作成していないので、例外が発生しなければOKとする

必要があれば画像を保存するようにし、手動で読み取れるかどうか確認する
"""

import unittest
from itertools import product

from mkmqr import create_symbol_image, ErrorCorrectionLevel as ECL, OverCapacityError


class TestImage(unittest.TestCase):
    dir_name = './test_dst_image'

    def setUp(self) -> None:
        # os.makedirs(self.dir_name)
        pass

    def tearDown(self) -> None:
        # os.remove(self.dir_name)
        pass

    def test_single_mode(self):
        texts = ['1111', 'AAAA', 'aaaa', 'ああああ']

        for text, ecl in product(texts, ECL):
            with self.subTest(f'{text} ({ecl})'):
                image = create_symbol_image(text, ecl)  # 例外が起きなければOK

    def test_mixed_mode(self):
        texts = ['11', 'AA', 'aa', 'ああ']

        for text1, text2, ecl in product(texts, texts, ECL):
            if text1 == text2:
                continue
            text = text1 + text2
            with self.subTest(f'{text} ({ecl})'):
                image = create_symbol_image(text, ecl)  # 例外が起きなければOK

    # ↓この辺りはoptimizeを直接叩いた方が良いかも

    def test_over_capacity_M4_L(self):
        """P31 PDF34"""
        ecl = ECL.L
        for char, capacity in zip(['1', 'A', 'a', 'あ'], [35, 21, 15, 9]):
            with self.subTest(f'{char} capacity({capacity})'):
                image = create_symbol_image(char * capacity, ecl)
            with self.subTest(f'{char} over capacity({capacity+1})'), self.assertRaises(OverCapacityError):
                image = create_symbol_image(char * (capacity + 1), ecl)

    def test_over_capacity_M4_M(self):
        """P31 PDF34"""
        ecl = ECL.M
        for char, capacity in zip(['1', 'A', 'a', 'あ'], [30, 18, 13, 8]):
            with self.subTest(f'{char} capacity({capacity})'):
                image = create_symbol_image(char * capacity, ecl)
            with self.subTest(f'{char} over capacity({capacity+1})'), self.assertRaises(OverCapacityError):
                image = create_symbol_image(char * (capacity + 1), ecl)

    def test_over_capacity_M4_Q(self):
        """P31 PDF34"""
        ecl = ECL.Q
        for char, capacity in zip(['1', 'A', 'a', 'あ'], [21, 13, 9, 5]):
            with self.subTest(f'{char} capacity({capacity})'):
                image = create_symbol_image(char * capacity, ecl)
            with self.subTest(f'{char} over capacity({capacity+1})'), self.assertRaises(OverCapacityError):
                image = create_symbol_image(char * (capacity + 1), ecl)

    # todo モード混在およびその容量をテストする　P97～ (PDF 100～)


if __name__ == '__main__':
    unittest.main()
