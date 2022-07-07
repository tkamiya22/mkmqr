import unittest

from mkmqr.model import Version, Mode, ErrorCorrectionLevel, Mask, values
from mkmqr.binary import bin2arr, concat_arr, bin2mat, merge_matrix
from mkmqr.matrix import *


class TestCodewordMatrix(unittest.TestCase):
    """JIS X0510 P91 (PDF 94) 附属書I.3"""

    version = Version.M2
    ecl = ErrorCorrectionLevel.L
    mode = Mode.Numeric

    text = '01234567'

    def test_1_1(self):
        """2進値に変換"""
        excepted = bin2arr(0b0000001100_0101011001_1000011, 27)
        actual = self.mode.encode(self.text)
        # self.assertEquals(excepted, actual)
        self.assertTrue((excepted == actual).all())

    def test_1_2(self):
        """モード指示子"""
        excepted = bin2arr(0b0, 1)
        actual = values.get_mode_indicator(self.version, self.mode)
        self.assertTrue((excepted == actual).all())

    def test_1_3(self):
        """文字数指示子"""
        excepted = bin2arr(0b1000, 4)
        actual = values.get_character_count_indicator(self.version, self.mode, len(self.text))
        self.assertTrue((excepted == actual).all())

    def test_1_4(self):
        """終端パターン"""
        excepted = bin2arr(0b00000, 5)
        actual = self.version.terminator
        self.assertTrue((excepted == actual).all())

    def test_1_5(self):
        """モード指示子、文字数指示子、2進データ、終端パターンを接続"""
        excepted = bin2arr(0b0_1000_0000001100_0101011001_1000011_00000, 37)

        mi = bin2arr(0b0, 1)
        cci = bin2arr(0b1000, 4)
        data = bin2arr(0b0000001100_0101011001_1000011, 27)
        terminator = bin2arr(0b00000, 5)
        actual = concat_arr([mi, cci, data, terminator])
        self.assertTrue((excepted == actual).all())

    def test_1_6(self):
        """埋め草ビットを追加"""
        excepted = bin2arr(0b01000000_00011000_10101100_11000011_00000000, 40)
        arr = bin2arr(0b0_1000_0000001100_0101011001_1000011_00000, 37)
        capacity = values.get_data_bit_capacity(self.version, self.ecl)
        actual = add_padding_bit(arr, capacity)
        self.assertTrue((excepted == actual).all())

    def test_1_7(self):
        """埋め草コード語は不要"""
        excepted = bin2arr(0b01000000_00011000_10101100_11000011_00000000, 40)
        arr = bin2arr(0b01000000_00011000_10101100_11000011_00000000, 40)
        capacity = values.get_data_bit_capacity(self.version, self.ecl)
        actual = add_padding_codeword(arr, capacity)
        self.assertTrue((excepted == actual).all())

    def test_2(self):
        """誤り訂正コード語"""
        excepted = bin2arr(0b10000110_00001101_00100010_10101110_00110000, 40)
        arr = bin2arr(0b01000000_00011000_10101100_11000011_00000000, 40)
        actual = get_error_correction_codeword(self.version, self.ecl, arr)
        self.assertTrue((excepted == actual).all())

    def test_3(self):
        """マトリックスにモジュールを配置"""
        excepted = bin2mat([
            0b1111111010101,
            0b1000001001100,
            0b1011101000011,
            0b1011101000001,
            0b1011101001101,
            0b1000001000000,
            0b1111111000001,
            0b0000000000010,
            0b1000000000000,
            0b0000100100100,
            0b1111101110000,
            0b0000100001000,
            0b1000101000110,
        ], 13)

        d_cw = bin2arr(0b01000000_00011000_10101100_11000011_00000000, 40)
        ec_cw = bin2arr(0b10000110_00001101_00100010_10101110_00110000, 40)
        cw = concat_arr([d_cw, ec_cw])

        mat_fp = get_function_pattern_matrix(self.version)
        mat_cw = place_codeword(self.version, cw)
        actual = merge_matrix([mat_fp, mat_cw])

        self.assertTrue((excepted == actual).all())

    def test_4(self):
        """マスク処理パターンの選択"""
        excepted = Mask.Mask01
        arr = bin2mat([
            0b1111111010101,
            0b1000001001100,
            0b1011101000011,
            0b1011101000001,
            0b1011101001101,
            0b1000001000000,
            0b1111111000001,
            0b0000000000010,
            0b1000000000000,
            0b0000100100100,
            0b1111101110000,
            0b0000100001000,
            0b1000101000110,
        ], 13)
        actual, _ = get_optimal_mask(arr)
        self.assertEqual(excepted, actual)

    def test_5(self):
        """形式情報"""
        excepted = bin2arr(0b101000010011001, 15)
        actual = values.get_format_information(self.version, self.ecl, Mask.Mask01)
        self.assertTrue((excepted == actual).all())

    def test_6(self):
        """最終的なシンボル"""
        excepted = bin2mat([
            0b1111111010101,
            0b1000001011101,
            0b1011101001101,
            0b1011101001111,
            0b1011101011100,
            0b1000001010001,
            0b1111111001111,
            0b0000000001100,
            0b1101000010001,
            0b0110101010101,
            0b1110011111110,
            0b0001010000110,
            0b1110100110111,
        ], 13)

        # 手順3の機能パターンとコード語列が配置された状態
        mat_cw = bin2mat([
            0b1111111010101,
            0b1000001001100,
            0b1011101000011,
            0b1011101000001,
            0b1011101001101,
            0b1000001000000,
            0b1111111000001,
            0b0000000000010,
            0b1000000000000,
            0b0000100100100,
            0b1111101110000,
            0b0000100001000,
            0b1000101000110,
        ], 13)
        mat_msk = get_mask_matrix(Mask.Mask01, mat_cw.shape)
        mat_fi = place_format_information(self.version, bin2arr(0b101000010011001, 15))
        actual = merge_matrix([mat_cw, mat_msk, mat_fi])
        self.assertTrue((excepted == actual).all())


if __name__ == '__main__':
    unittest.main()
