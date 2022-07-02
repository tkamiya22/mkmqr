"""
形式情報の行列を生成するプログラム
"""

from logging import getLogger

from ..binary import BinaryArray, BinaryMatrix, empty_matrix, arr2str
from ..model import Version, ErrorCorrectionLevel as ECL, Mask, values

logger = getLogger(__name__)


def place_format_information(version: Version, format_information: BinaryArray) -> BinaryMatrix:
    """形式情報を行列に配置"""
    def idx():
        for i in range(1, 8):
            yield 8, i
        for i in range(8, 0, -1):
            yield i, 8

    mat = empty_matrix(version.size)
    for (i, j), fi in zip(idx(), format_information):
        mat[i, j] = fi
    return mat


def get_format_information_matrix(version: Version, ecl: ECL, mask: Mask) -> BinaryMatrix:
    """形式情報を配置した行列を取得"""
    fi = values.get_format_information(version, ecl, mask)
    logger.info(f'format information: ' + arr2str(fi, byte_sep=' '))
    return place_format_information(version, fi)
