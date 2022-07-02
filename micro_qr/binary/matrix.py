"""
真偽値の行列を扱うためのファイル
"""

from typing import Iterable, Union, Tuple
import numpy as np

BinaryMatrix = np.ndarray
"""バイナリ形式の行列"""

_dtype = bool
"""データ型"""


def bin2mat(binaries: Iterable[int], capacity: int) -> BinaryMatrix:
    """
    自然数のビット列を行列に変換する

    :param binaries: 変換する自然数
    :param capacity: 列方向の容量
    :return: 変換後の行列
    """

    if any((b < 0 for b in binaries)):
        raise ValueError(f'binary must be greater than or equal to 0 (index: {[b < 0 for b in binaries].index(True)})')
    if any((b >> capacity != 0 for b in binaries)):
        raise ValueError(f'overflow (index: {[b >> capacity != 0 for b in binaries].index(True)})')

    return np.array([
        [
            binary & (1 << shift) != 0
            for shift in reversed(range(capacity))
        ]
        for binary in binaries
    ], dtype=_dtype)


def mat2str(matrix: BinaryMatrix, on: str = '＠', off: str = '　', row_sep: str = '\n', col_sep: str = '') -> str:
    """
    行列を文字列に変換する

    :param matrix: 変換する行列
    :param on: ビットが立っていることを表す文字
    :param off: ビットが立っていないことを表す文字
    :param row_sep: 行の区切り文字
    :param col_sep: 列の区切り文字
    :return: 変換後の文字列
    """
    return row_sep.join(
        col_sep.join(on if x else off for x in row)
        for row in matrix
    )


def merge_matrix(matrix: Iterable[BinaryMatrix]) -> BinaryMatrix:
    """
    複数の行列をまとめ上げる

    :param matrix: まとめる行列
    :return: まとめ上げた行列
    """
    return np.logical_xor.reduce(matrix, dtype=_dtype)


def toggle_matrix(matrix: BinaryMatrix) -> BinaryMatrix:
    """
    行列の全ての要素を反転する

    :param matrix: 反転する行列
    :return: 反転した行列
    """
    return np.logical_not(matrix)


def empty_matrix(size: Union[int, Tuple[int, int]]):
    """
    空の行列を作成する

    :param size: 行列の大きさ (値を1つのみ指定した場合は正方行列となる)
    :return: 空の行列
    """
    if isinstance(size, int):
        size = size, size
    return np.zeros(size, dtype=bool)
