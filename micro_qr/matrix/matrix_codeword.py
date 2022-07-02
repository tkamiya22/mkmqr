"""
コード語列を表す行列を作成するプログラム
"""

from logging import getLogger

from ..binary import bin2arr, concat_arr, BinaryArray, BinaryMatrix, arr2bin, empty_matrix, arr2str
from ..error_correction import ReedSolomonCode, ResidueFieldOperator, PolynomialRing
from ..model import Version, ErrorCorrectionLevel as ECL, OverCapacityError, values
from ..util import Case

logger = getLogger(__name__)


def padding_to_8bit(arr: BinaryArray) -> BinaryArray:
    """8bitの倍数になるように末尾に0を追加する"""
    n = len(arr) % 8
    n = (8 - n) % 8
    return concat_arr([arr, bin2arr(0, n)])


# region データコード語
def add_terminator(version: Version, arr: BinaryArray, capacity: int) -> BinaryArray:
    """
    配列に終端パターンを追加

    :param version: 型番
    :param arr: 終端パターンを追加する配列
    :param capacity: ビット単位の容量
    :return: 終端パターンを追加した配列
    """
    arr = concat_arr([arr, version.terminator])
    return arr[:capacity]


def add_padding_bit(arr: BinaryArray, capacity: int):
    """
    配列に埋め草ビットを追加

    :param arr: 埋め草ビットを追加する配列
    :param capacity: ビット単位の容量
    :return: 埋め草ビットを追加した配列
    """
    arr = padding_to_8bit(arr)
    return arr[:capacity]


def add_padding_codeword(arr: BinaryArray, capacity: int):
    """
    配列に埋め草コード語を追加

    :param arr: 埋め草コード語を追加する配列
    :param capacity: ビット単位の容量
    :return: 埋め草コード語を追加した配列
    """
    padding_codeword_num, remaining = divmod(capacity - len(arr), 8)  # remainingは 0 or 4
    cw = [
        bin2arr(0b1110_1100, 8) if i % 2 == 0 else bin2arr(0b0001_0001, 8)
        for i in range(padding_codeword_num)
    ]
    return concat_arr([arr] + cw + [bin2arr(0, remaining)])


def segment2data_codeword(version: Version, ecl: ECL, segment: BinaryArray) -> BinaryArray:
    """セグメントをデータコード語に変換"""
    logger.debug(f'[convert segment to data codeword]')

    capacity = values.get_data_bit_capacity(version, ecl)
    if len(segment) > capacity:
        raise OverCapacityError(f'Segment({len(segment)}-bit) is over capacity({capacity}-bit)', segment)

    arr = segment
    logger.debug(f'segment: {len(segment)}/{capacity} bits')
    arr = add_terminator(version, arr, capacity)
    logger.debug(f'add terminator: {len(arr)}/{capacity} bits')
    arr = add_padding_bit(arr, capacity)
    logger.debug(f'add remaining bit: {len(arr)}/{capacity} bits')
    arr = add_padding_codeword(arr, capacity)
    logger.debug(f'add remaining codeword: {len(arr)}/{capacity} bits')

    return arr
# endregion


# region 誤り訂正コード語
def get_generator_polynomial(rf_op: ResidueFieldOperator, degree: int):
    """
    生成多項式を取得

    :param rf_op: 剰余環として扱うためのインスタンス
    :param degree: 生成多項式の次数
    :return: 生成多項式
    """
    def exp2gen(*exp: int):
        return [rf_op.from_exp(e) for e in exp]

    return Case(degree)\
        .when(2, exp2gen(0, 25, 1))\
        .when(5, exp2gen(0, 113, 164, 166, 119, 10))\
        .when(6, exp2gen(0, 166, 0, 134, 5, 176, 15))\
        .when(8, exp2gen(0, 175, 238, 208, 249, 215, 252, 196, 28))\
        .when(10, exp2gen(0, 251, 67, 46, 61, 118, 70, 64, 94, 32, 45))\
        .when(14, exp2gen(0, 199, 249, 155, 48, 190, 124, 218, 137, 216, 87, 207, 59, 22, 91))\
        .value


def setup_rs_code(version: Version, ecl: ECL) -> ReedSolomonCode:
    """RS符号を計算するためのインスタンスを取得"""
    primitive_poly = PolynomialRing(0b1_0001_1101)
    rf_op = ResidueFieldOperator(primitive_poly)
    degree = values.get_error_correction_codeword_num(version, ecl)
    generator_poly = get_generator_polynomial(rf_op, degree)
    return ReedSolomonCode(rf_op, generator_poly)


def get_error_correction_codeword(version: Version, ecl: ECL, data_codeword: BinaryArray) -> BinaryArray:
    """
    データコード語から誤り訂正コード語を取得

    :param version: 型番
    :param ecl: 誤り訂正レベル
    :param data_codeword: 誤り訂正コード語を計算する対象のデータコード語
    :return: 計算した誤り訂正コード語
    """
    data_codeword = padding_to_8bit(data_codeword)  # 末尾が4bitでも8bitに合わせる
    poly = [PolynomialRing(arr2bin(data_codeword[i:i+8])) for i in range(0, len(data_codeword), 8)]  # 8bitごとに区切る

    rs_code = setup_rs_code(version, ecl)
    ecc = rs_code.encode(poly)
    return concat_arr([bin2arr(e.coefficient, 8) for e in ecc])
# endregion


# region 行列
def place_codeword(version: Version, codeword: BinaryArray) -> BinaryMatrix:
    """
    コード語列を行列に配置

    :param version: 型番
    :param codeword: コード語列
    :return:
    """
    n = version.size
    if len(codeword) != (n-1)**2 - 8**2:
        raise ValueError(f'Codewords must be {(n-1)**2 - 8**2}bit, but it is {len(codeword)}bit', codeword)

    def cursor():
        """
        ビットを配置する座標(i,j)を順に返す
        原点は左上、iは下方向、jは右方向
        """
        for idx, j in enumerate(range(n-1, 0, -2)):
            rng = range(9, n) if j <= 8 else range(1, n)  # j<=8のときは切り出しパターンを避けなければならない
            if idx % 2 == 0:  # 最初は上方向(iの減少方向)に配置していく
                rng = reversed(rng)  # 上下に往復するように配置するため、向きを反転する
            for i in rng:  # ジグザグに蛇行して配置していく
                yield i, j
                yield i, j-1

    code = empty_matrix(n)
    for (i, j), c in zip(cursor(), codeword):
        code[i, j] = c
    return code


def segment2matrix(version: Version, ecl: ECL, segment: BinaryArray) -> BinaryMatrix:
    """
    セグメントを行列に変換

    :param version: 型番
    :param ecl: 誤り訂正レベル
    :param segment: セグメント
    :return: セグメントの情報を格納した行列
    """
    data_codeword = segment2data_codeword(version, ecl, segment)
    ec_codeword = get_error_correction_codeword(version, ecl, data_codeword)
    codeword = concat_arr([data_codeword, ec_codeword])
    logger.info('codewords: ' + arr2str(data_codeword, byte_sep=' ') + ', ' + arr2str(ec_codeword, byte_sep=' '))
    mat_codeword = place_codeword(version, codeword)
    return mat_codeword
# endregion
