"""
それぞれのパーツを結合してマイクロQRコードを表す行列を生成するプログラム
"""

from logging import getLogger

from PIL import Image

from ..binary import BinaryMatrix, merge_matrix, empty_matrix, toggle_matrix, BinaryArray
from ..matrix import segment2matrix, get_optimal_mask, get_format_information_matrix, get_function_pattern_matrix
from ..model import Version, ErrorCorrectionLevel as ECL
from ..optimization import analyze_text

logger = getLogger(__name__)


# region セグメントから画像まで
def add_quiet_zone(code: BinaryMatrix, size: int) -> BinaryMatrix:
    """
    クワイエットゾーンを追加

    :param code: コード
    :param size: クワイエットゾーンの幅 (2以上を推奨)
    :return: クワイエットゾーンを追加したコード
    """
    if size < 0:
        raise ValueError('size must be greater than or equal to 0', size)

    h, w = code.shape
    mat = empty_matrix((h + 2 * size, w + 2 * size))
    mat[size:size + h, size:size + w] = code
    return mat


def segment2symbol_matrix(version: Version, ecl: ECL, segment: BinaryArray) -> BinaryMatrix:
    """
    セグメントからマイクロQRコードの行列を作成

    :param version: 型番
    :param ecl: 誤り訂正レベル
    :param segment: セグメント
    :return: マイクロQRコードの行列
    """
    mat_codeword = segment2matrix(version, ecl, segment)
    mask, mat_mask = get_optimal_mask(mat_codeword)
    mat_fi = get_format_information_matrix(version, ecl, mask)
    mat_fp = get_function_pattern_matrix(version)

    code = merge_matrix([mat_fp, mat_fi, mat_codeword, mat_mask])
    return code


def symbol_matrix2image(matrix: BinaryMatrix, size: int = None, quiet_zone: int = 2) -> Image.Image:
    """
    マイクロQRコードの行列から画像を生成

    :param matrix: 行列
    :param size: 画像の一辺のピクセル数 (省略すると1セルが10ピクセルとなるサイズ)
    :param quiet_zone: クワイエットゾーンの幅 (2以上を推奨)
    :return: 画像
    """
    matrix = add_quiet_zone(matrix, quiet_zone)
    matrix = toggle_matrix(matrix)
    img = Image.fromarray(matrix)
    if size is None:
        size = img.height * 10
    img = img.resize((size, size), resample=Image.Resampling.NEAREST)
    return img


# segment2image  # 書いても2行だから難しくはない、引数に変更があった時に大変そう？
# endregion


# region 型番など自動識別
def create_symbol_matrix(text: str, ecl: ECL = ECL.NONE) -> BinaryMatrix:
    """
    テキストからマイクロQRコードの行列を作成

    :param text: テキスト
    :param ecl: 誤り訂正レベル
    :return: マイクロQRコードを表す行列
    """
    version, ecl, segment = analyze_text(text, ecl=ecl)
    return segment2symbol_matrix(version, ecl, segment)


def create_symbol_image(text: str, ecl: ECL = ECL.NONE, size: int = None) -> Image.Image:
    """
    テキストからマイクロQRコードの画像を作成

    :param text: テキスト
    :param ecl: 誤り訂正レベル
    :param size: 画像の一辺の長さ
    :return:
    """
    matrix = create_symbol_matrix(text, ecl)
    return symbol_matrix2image(matrix, size, 2)
# endregion


# 型番などを指定して作成する関数は必要？
# モードは自動指定しない方が良い？（8ビットバイトモードがかな漢字を含まないため）
# 型番と誤り訂正レベルとテキストを引数とする？
