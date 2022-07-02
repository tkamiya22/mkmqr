import itertools
from copy import deepcopy
from logging import getLogger
from math import inf
from typing import List

from ..text_model import GroupedText, ModeText
from ..util import list2str, grouping
from ...model import Mode, Version

logger = getLogger(__name__)


def _get_merged_mode(mode1: Mode, mode2: Mode) -> Mode:
    modes = (mode1, mode2)
    if modes == (Mode.Kanji, Mode.Kanji):
        return Mode.Kanji
    elif Mode.Kanji in modes or Mode.EightBitByte in modes:
        return Mode.EightBitByte
    elif Mode.AlphaNumeric in modes:
        return Mode.AlphaNumeric
    else:
        return Mode.Numeric


def _merge_edges(grouped: GroupedText, edges_to_merge: List[bool]):
    """
    指定の境界でグループを結合する (破壊操作)

    :param grouped: グループ化したテキスト (破壊操作)
    :param edges_to_merge: 結合する境界 (破壊操作)
    """
    logger.debug('edges: ' + list2str(edges_to_merge))
    logger.debug('grouped: ' + list2str(grouped))

    edge = 0
    while edge < len(grouped) - 1:  # 長さが変わるためforではなくwhileでループ
        if edges_to_merge[edge]:
            logger.debug(f'- merged at edge {edge}')

            grouped[edge + 1] = ModeText(
                _get_merged_mode(grouped[edge].mode, grouped[edge + 1].mode),
                grouped[edge].text + grouped[edge + 1].text
            )

            # popでインデックスが1つずれるのでedgeはインクリメントしない
            grouped.pop(edge)
            edges_to_merge.pop(edge)
        else:
            logger.debug(f'- not merged at edge {edge}')
            edge += 1  # 次の境界へ

        logger.debug('edges: ' + list2str(edges_to_merge))
        logger.debug('grouped: ' + list2str(grouped))


def optimize_brute_force(version: Version, text: str) -> GroupedText:
    """
    最もビット数が短くなるように指定のテキストをグループ化する

    :param version: 型番
    :param text: テキスト
    :return: ビット数が最短となる区切りのグループ
    """
    # memo グループ数nに対して2**(n-1)回のループを行うため、重くなりやすい 取り扱いに注意
    logger.debug(f'[optimize by brute force]')

    grouped = GroupedText(grouping(text))
    edge_num = len(grouped) - 1

    best_grouped = ...
    best_length = inf

    for edges_to_merge in itertools.product([True, False], repeat=edge_num):
        grp = deepcopy(grouped)  # 元のgroupedを破壊しないようにコピー
        egs = list(edges_to_merge)  # tupleは操作が効かないのでlistへ
        _merge_edges(grp, egs)

        ln = grp.get_segment_length(version)
        if ln < best_length:
            best_grouped = grp
            best_length = ln

        x = '*' if ln == best_length else ' '
        logger.debug(f'{x} result {ln:3}bits {list2str(grp)}')

    logger.info(f'{best_length}bits {list2str(best_grouped)}')
    return best_grouped
