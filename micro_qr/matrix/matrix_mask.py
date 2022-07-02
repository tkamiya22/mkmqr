"""
マスクの行列を生成するプログラム
"""

import itertools
from logging import getLogger
from typing import Tuple, Union

from ..binary import BinaryMatrix, empty_matrix
from ..model import Mask

logger = getLogger(__name__)


def get_mask_matrix(mask: Mask, size: Union[int, Tuple[int, int]]) -> BinaryMatrix:
    """
    マスクを取得

    :param mask: マスクの種類
    :param size: 行列の大きさ
    :return: マスクの行列
    """

    def func(tup):
        i, j = tup

        # データ領域以外はマスクしない
        if i == 0 or j == 0:  # タイミングパターン
            return False
        if i <= 8 and j <= 8:  # 切り出しシンボル・分離パターン・形式情報
            return False

        return mask.function(i, j)  # マスクパターン

    mat = empty_matrix(size)
    h, w = mat.shape
    idx = tuple(zip(*filter(func, itertools.product(range(h), range(w)))))
    mat[idx] = True
    return mat


def calc_mask_score(matrix: BinaryMatrix) -> int:
    """
    マスクの点数を計算

    :param matrix: 点数を計算する行列
    :return: 得点(高い方が良い)
    """
    s1 = sum(matrix[-1, 1:])
    s2 = sum(matrix[1:, -1])
    return min(s1, s2) * 16 + max(s1, s2)


def get_optimal_mask(code: BinaryMatrix) -> Tuple[Mask, BinaryMatrix]:
    """最適なマスクを取得"""

    best_mask: Tuple[Mask, BinaryMatrix] = ...
    best_score = -1

    logger.debug(f'[select optimal mask]')
    for mask in Mask:
        mat_mask = get_mask_matrix(mask, code.shape)
        score = calc_mask_score(mat_mask ^ code)
        logger.debug(f'- {mask}: {score:3}')
        if score > best_score:
            best_mask = mask, mat_mask
            best_score = score

    logger.info(f'selected mask: {best_mask[0]}')
    return best_mask
