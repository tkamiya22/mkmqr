import itertools
from math import inf

from ..text_model import SeparatedModeText, GroupedText
from ..util import grouping
from ...model import Version


def _opt_c_hc(version: Version, separated: SeparatedModeText) -> GroupedText:
    if len(separated) <= 1:
        return GroupedText([separated])  # 切るところがない場合

    best_grouped: GroupedText = ...
    best_bit_len = inf

    for left, right in itertools.combinations(range(len(separated)), 2):
        grouped = GroupedText(filter(
            lambda x: len(x) != 0, [separated[:left], separated[left:right], separated[right:]]
        ))
        bit_len = grouped.get_segment_length(version)
        if bit_len < best_bit_len:  # todo 等号のありなしを検討
            best_grouped = grouped
            best_bit_len = bit_len

    no_cut_bit_len = separated.get_segment_length(version)
    if no_cut_bit_len <= best_bit_len:  # todo 等号のありなしを検討
        return GroupedText([separated])  # 切らない方が良い場合

    return GroupedText(itertools.chain.from_iterable([_opt_c_hc(version, txt) for txt in best_grouped]))


def optimize_hill_climbing(version: Version, text: str) -> GroupedText:
    return _opt_c_hc(version, SeparatedModeText(grouping(text)))
