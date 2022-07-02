"""
機能パターンの行列を作成するプログラム
"""

from ..binary import BinaryMatrix, empty_matrix
from ..model import Version


def get_function_pattern_matrix(version: Version) -> BinaryMatrix:
    """機能パターンの行列を取得"""
    ptn = empty_matrix(version.size)
    # タイミングパターン
    ptn[::2, 0] = True
    ptn[0, ::2] = True
    # 機能パターン
    ptn[0:7, 0:7] = True
    ptn[1:6, 1:6] = False
    ptn[2:5, 2:5] = True
    return ptn
