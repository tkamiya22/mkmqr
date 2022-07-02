"""
符号化後の2進データが最短になるようにテキストを解析するプログラム
"""


from logging import getLogger
from typing import List, Tuple, Union, Container

from .algorithm import optimize
from .util import char2mode, list2str
from ..binary import BinaryArray, concat_arr, arr2str
from ..model import Version, ErrorCorrectionLevel as ECL, values, OverCapacityError, InvalidPairError

logger = getLogger(__name__)


def text2mixing_segment(version: Version, text: str) -> BinaryArray:
    grouped = optimize(version, text)
    logger.debug(f'({version}, {text}) -> {grouped}')
    return concat_arr([sub.get_segment(version) for sub in grouped])


def text2mixing_segment_length(version: Version, text: str):
    grouped = optimize(version, text)
    return sum((sub.get_segment_length(version) for sub in grouped))


def analyze_text(
        text: str, version: Union[Version, Container[Version]] = ..., ecl: Union[ECL, Container[ECL]] = ...
) -> Tuple[Version, ECL, BinaryArray]:
    """
    テキストを解析して最適な型番、誤り訂正レベル、セグメントを計算する

    :param text: テキスト
    :param version: 最大の型番 (あるいは使用してもよい型番の一覧)
    :param ecl: 必要な誤り訂正レベル (あるいは使用してもよい誤り訂正レベルの一覧)
    :return: 型番, 誤り訂正レベル, セグメント
    """
    # region 前処理  # これ以降は引数のversion,eclを使用しない 一覧を表すversions,eclsを使用する
    from typing import TypeVar
    T = TypeVar('T')

    def parse_arg(arg: Union[T, Container[T]], reference: List[T]) -> List[T]:  # ...の型が上手く表せなかった
        if arg is ...:
            return reference  # そのまま返す
        elif isinstance(arg, Container):
            return [x for x in reference if x in arg]  # 共通部分だけを返す
        else:
            return reference[:reference.index(arg)+1]  # argまでを返す

    versions = parse_arg(version, [Version.M1, Version.M2, Version.M3, Version.M4])
    """探索順を考慮した型番の一覧"""
    ecls = parse_arg(ecl, [ECL.Q, ECL.M, ECL.L, ECL.NONE])
    """探索順を考慮した誤り訂正レベルの一覧"""
    modes = {char2mode(c) for c in text}
    """使用されているモードの一覧"""

    logger.debug(f'versions: {list2str(versions)}')
    logger.debug(f'ecls: {list2str(ecls)}')
    logger.debug(f'modes: {list2str(modes)}')
    # endregion

    # region M1は特殊なので別途処理  # これ以降は_version,_eclを個別の要素を表すために使用する
    _version = Version.M1
    """注目する型番"""
    _ecl = ECL.NONE
    """注目する誤り訂正レベル"""

    if _version in versions and _ecl in ecls:
        if values.check_combination(version=version, ecl=ecl, mode=modes):
            seg_len = text2mixing_segment_length(_version, text)
            capacity = values.get_data_bit_capacity(_version, _ecl)
            if seg_len <= capacity:
                segment = text2mixing_segment(_version, text)
                return _version, _ecl, segment
        else:
            logger.debug(f'{_version}: invalid pair')

    # M1と誤り検出のみはこの組み合わせでしか使えないため一覧から除外する
    if _version in versions:
        versions.remove(_version)
    if _ecl in ecls:
        ecls.remove(_ecl)

    # 型番と誤り訂正レベルのいずれかが空になってしまったら終了
    if len(versions) == 0 or len(ecls) == 0:
        raise InvalidPairError('there is no pair that meets the conditions')
    # endregion

    # region 型番の選択  # ここで_versionが確定する
    exists_valid_pair = False  # 容量が不足しているのか、設定が不正なのかを区別するため
    _ecl = ecls[-1]  # 一番容量が多い(=低い)レベルで試す
    logger.debug(f'select version from {list2str(versions)} (lowest ecl: {_ecl})')

    for _version in versions:
        if not values.check_combination(version=_version, ecl=_ecl, mode=modes):
            logger.debug(f'{_version}: invalid pair')
            continue
        exists_valid_pair = True  # 少なくとも1つは有効な組み合わせが存在した

        seg_len = text2mixing_segment_length(_version, text)
        capacity = values.get_data_bit_capacity(_version, _ecl)
        if seg_len > capacity:
            logger.debug(f'{_version}: over capacity')
            continue

        logger.debug(f'{_version}: OK')
        break  # 容量に収まればループを打ち切って型番を確定する (次の工程の番兵を求めるだけなので、セグメントはまだ求めない)
    else:
        # breakされなかった場合 (=条件を満たす組み合わせが存在しなかった場合)
        if exists_valid_pair:
            raise OverCapacityError('there was a pair that met the conditions, but there was not enough capacity')
        else:
            raise InvalidPairError('there is no pair that meets the conditions')
    # endregion

    # region 誤り訂正レベル  # 求めた_versionに_eclをすり合わせる
    logger.debug(f'select ecl from {list2str(ecls)} (version: {_version})')
    for _ecl in ecls:
        if not values.check_combination(version=_version, ecl=_ecl, mode=modes):
            logger.debug(f'{_ecl}: invalid pair')
            continue

        seg_len = text2mixing_segment_length(_version, text)
        capacity = values.get_data_bit_capacity(_version, _ecl)
        if seg_len > capacity:
            logger.debug(f'{_ecl}: over capacity')
            continue

        segment = text2mixing_segment(_version, text)
        logger.debug(f'{_ecl}: OK')
        logger.info(f'analyzed result: {_version}, {_ecl}')
        logger.info(f'binary data: {arr2str(segment)} ({len(segment)} / {capacity} bits)')
        return _version, _ecl, segment

    raise RuntimeError('it never come here')  # 型番の選択結果が番兵となるため、ここには絶対に来ないはず
    # endregion


