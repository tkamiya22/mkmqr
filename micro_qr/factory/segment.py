"""
テキストを指定のモードでセグメントに変換するプログラム
"""

from logging import getLogger

from ..binary import concat_arr, BinaryArray, arr2str
from ..model import Version, Mode, values

logger = getLogger(__name__)


def data2segment(version: Version, mode: Mode, data: BinaryArray, character_count: int) -> BinaryArray:
    """2進データをセグメントに変換"""
    mi = values.get_mode_indicator(version, mode)
    cci = values.get_character_count_indicator(version, mode, character_count)
    logger.debug(f'segment: (mi: {arr2str(mi)})(cci: {arr2str(cci)})(data: {arr2str(data)})')
    return concat_arr([mi, cci, data])


def text2segment(version: Version, mode: Mode, text: str) -> BinaryArray:
    """テキストをセグメントに変換"""
    data = mode.encode(text)
    cc = mode.character_count(text)
    return data2segment(version, mode, data, cc)
