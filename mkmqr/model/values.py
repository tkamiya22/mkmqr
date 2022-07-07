from typing import Set, Union

from .error import OverCapacityError, InvalidPairError
from ..binary import concat_arr, bin2arr, BinaryArray
from ..error_correction import PolynomialRing
from ..model import Version, ErrorCorrectionLevel as ECL, Mask, Mode
from ..util import Case


# todo 1つから決まる値はEnumに持たせているが、表記の統一のためここに移すか検討する


# region 組み合わせで決まる値
def _assert_mode(version: Version, mode: Mode) -> None:
    """
    型番とモードの組み合わせが妥当か検証

    :raise InvalidPairError: 不適切な組み合わせが与えられたとき
    """
    if version == Version.M1 and mode != Mode.Numeric:
        raise InvalidPairError('M1 only supports number mode')
    if version == Version.M2 and mode not in [Mode.Numeric, Mode.AlphaNumeric]:
        raise InvalidPairError('M2 only supports number mode and alphanumeric mode')


def get_data_bit_capacity(version: Version, ecl: ECL) -> int:
    """
    データ容量をビット単位で取得

    P31 (PDF 34) 表7

    :param version: 型番
    :param ecl: 誤り訂正レベル
    :return: データ容量(ビット単位)
    """
    return Case([version, ecl]) \
        .when([Version.M1, ECL.NONE], 20) \
        .when([Version.M2, ECL.L], 40) \
        .when([Version.M2, ECL.M], 32) \
        .when([Version.M3, ECL.L], 84) \
        .when([Version.M3, ECL.M], 68) \
        .when([Version.M4, ECL.L], 128) \
        .when([Version.M4, ECL.M], 112) \
        .when([Version.M4, ECL.Q], 80) \
        .value


def get_error_correction_codeword_num(version: Version, ecl: ECL) -> int:
    """
    誤り訂正コード語の総数を取得

    P36 (PDF 39) 表9

    :param version: 型番
    :param ecl: 誤り訂正レベル
    :return: 誤り訂正コード語の総数
    """
    return Case([version, ecl]) \
        .when([Version.M1, ECL.NONE], 2) \
        .when([Version.M2, ECL.L], 5) \
        .when([Version.M2, ECL.M], 6) \
        .when([Version.M3, ECL.L], 6) \
        .when([Version.M3, ECL.M], 8) \
        .when([Version.M4, ECL.L], 8) \
        .when([Version.M4, ECL.M], 10) \
        .when([Version.M4, ECL.Q], 14) \
        .value


def get_symbol_number(version: Version, ecl: ECL) -> int:
    """
    シンボル番号を取得

    P55 (PDF 58) 表13

    :param version: 型番
    :param ecl: 誤り訂正レベル
    :return: シンボル番号
    """
    lst = [
        (Version.M1, ECL.NONE),
        (Version.M2, ECL.L),
        (Version.M2, ECL.M),
        (Version.M3, ECL.L),
        (Version.M3, ECL.M),
        (Version.M4, ECL.L),
        (Version.M4, ECL.M),
        (Version.M4, ECL.Q),
    ]
    return lst.index((version, ecl))


def get_format_information(version: Version, ecl: ECL, mask: Mask) -> BinaryArray:
    """
    形式情報を取得

    P55 (PDF 58) 7.9.2

    :param version: 型番
    :param ecl: 誤り訂正レベル
    :param mask: マスク
    :return: 形式情報のビット列
    """
    symbol_number = get_symbol_number(version, ecl)
    fi = symbol_number << 2 | mask.mask_pattern_value
    fi_poly = PolynomialRing(fi << 10)
    gp = PolynomialRing(0b101_0011_0111)
    bch = (fi_poly % gp).coefficient
    x = concat_arr([bin2arr(fi, 5), bin2arr(bch, 10)])
    m = bin2arr(0b100010001000101, 15)
    return x ^ m


def get_mode_indicator(version: Version, mode: Mode) -> BinaryArray:
    """
    モード指示子を取得

    P21 (PDF 24) 表2

    :param version: 型番
    :param mode: モード
    :return: モード指示子のビット列
    """
    _assert_mode(version, mode)

    mi_len = version.mode_indicator_length
    mi_val = mode.mode_indicator_value
    return bin2arr(mi_val, mi_len)


def get_character_count_indicator_length(version: Version, mode: Mode) -> int:
    """
    文字数指示子のビット数を取得

    P21 (PDF 24) 表3

    :param version: 型番
    :param mode: モード
    :return: 文字数指示子のビット数
    """
    _assert_mode(version, mode)

    cci_len = Case([version, mode]) \
        .when([Version.M1, Mode.Numeric], 3) \
        .when([Version.M2, Mode.Numeric], 4) \
        .when([Version.M2, Mode.AlphaNumeric], 3) \
        .when([Version.M3, Mode.Numeric], 5) \
        .when([Version.M3, Mode.AlphaNumeric], 4) \
        .when([Version.M3, Mode.EightBitByte], 4) \
        .when([Version.M3, Mode.Kanji], 3) \
        .when([Version.M4, Mode.Numeric], 6) \
        .when([Version.M4, Mode.AlphaNumeric], 5) \
        .when([Version.M4, Mode.EightBitByte], 5) \
        .when([Version.M4, Mode.Kanji], 4) \
        .value
    return cci_len


def get_character_count_indicator(version: Version, mode: Mode, character_count: int) -> BinaryArray:
    """
    文字数指示子を取得

    P21 (PDF 24) 表3

    :param version: 型番
    :param mode: モード
    :param character_count: 文字数
    :return: 文字数指示子のビット列
    """
    cci_len = get_character_count_indicator_length(version, mode)
    try:
        return bin2arr(character_count, cci_len)
    except ValueError as err:
        raise OverCapacityError() from err
# endregion


# region 組み合わせの確認
def _check_combination_ve(version: Version, ecl: ECL) -> bool:
    """
    型番と誤り訂正レベルの組み合わせが有効か確認する

    P31 (PDF 34) 表7, P36 (PDF 39) 表9 等

    :param version: 型番
    :param ecl: 誤り訂正レベル
    :return: 組み合わせが有効か？
    """
    if version == Version.M1 and ecl != ECL.NONE:
        # logger.debug(f'M1 supports only error detection')
        return False  # M1は誤り検出のみ

    if ecl == ECL.NONE and version != Version.M1:
        # logger.debug(f'error detection supports only M1')
        return False  # 誤り検出はM1のみ

    if ecl == ECL.Q and version != Version.M4:
        # logger.debug(f'Level Q supports only M4')
        return False  # 誤り訂正レベルQはM4のみ

    return True


def _check_combination_vm(version: Version, mode: Union[Mode, Set[Mode]]) -> bool:
    """
    型番とモードの組み合わせが有効か確認する

    P18 (PDF 21) 7.3, P21 (PDF 24) 表2,3 等

    :param version: 型番
    :param mode: モード
    :return: 組み合わせが有効か？
    """
    modes = {mode} if isinstance(mode, Mode) else mode

    if version == Version.M1 and not modes <= {Mode.Numeric}:
        # logger.debug(f'M1 supports only Numeric mode')
        return False  # M1は数字モードのみ

    if version == Version.M2 and not modes <= {Mode.Numeric, Mode.AlphaNumeric}:
        # logger.debug(f'M2 supports only Numeric mode and AlphaNumeric mode')
        return False  # M2は数字モードと英数字モードのみ

    return True


def check_combination(*, version: Version = None, ecl: ECL = None, mode: Union[Mode, Set[Mode]] = None) -> bool:
    """
    組み合わせが有効か確認する

    :param version: 型番
    :param ecl: 誤り訂正レベル
    :param mode: モード
    :return: 組み合わせが有効か？
    """
    if version is not None and ecl is not None:
        if not _check_combination_ve(version, ecl):
            return False

    if version is not None and mode is not None:
        if not _check_combination_vm(version, mode):
            return False

    return True
# endregion
