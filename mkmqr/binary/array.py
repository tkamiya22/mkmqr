"""
真偽値の配列を扱うためのファイル
"""

from typing import Iterable
import numpy as np

BinaryArray = np.ndarray
"""バイナリ形式の配列"""

_dtype = bool
"""データ型"""


def arr2bin(array: BinaryArray) -> int:
    """
    配列のビット列を自然数に変換する

    :param array: 変換する配列
    :return: 変換後の自然数
    """
    return int(array.dot(2**np.arange(array.size)[::-1]))


def bin2arr(binary: int, capacity: int) -> BinaryArray:
    """
    自然数のビットを配列に変換する

    :param binary: 変換する自然数
    :param capacity: ビットの容量
    :return: 変換後の配列
    """
    if binary < 0:
        raise ValueError(f'binary must be greater than or equal to 0', binary)
    if binary >> capacity != 0:
        raise ValueError(f'overflow ({binary:b} : {capacity} bits)', binary, capacity)

    return np.array([
        binary & (1 << shift) != 0
        for shift in reversed(range(capacity))
    ], dtype=_dtype)


def arr2str(array: BinaryArray, on: str = '1', off: str = '0', byte_sep: str = '') -> str:
    """
    配列を文字列に変換する

    :param array: 変換する配列
    :param on: ビットが立っていることを表す文字
    :param off: ビットが立っていないことを表す文字
    :param byte_sep: 1バイトごとに挿入する区切り文字
    :return: 0,1から成る文字列
    """
    s = ''.join((on if b else off for b in array))
    s = byte_sep.join((s[i:i+8] for i in range(0, len(s), 8)))
    return s


def concat_arr(arrays: Iterable[BinaryArray]):
    """
    配列を連結する

    :param arrays: 連結する配列のリスト
    :return: 連結した配列
    """
    return np.concatenate(arrays, dtype=_dtype)
