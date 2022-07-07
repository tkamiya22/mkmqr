from typing import Iterable

from .text_model import GroupedText, ModeText
from ..model import Mode, InvalidCharacterError


def char2mode(char: str) -> Mode:
    """
    文字に対応している最も低位のモードを取得する

    :param char: 文字
    :return: 対応するモード
    """
    modes = [
        Mode.Numeric,
        Mode.AlphaNumeric,
        Mode.Kanji,
        Mode.EightBitByte,
    ]
    for mode in modes:
        if mode.is_valid(char):
            return mode
    raise InvalidCharacterError(f'Invalid character', char)


def grouping(text: str) -> GroupedText:
    """
    同じモードが連続する箇所でグループ化する

    :param text: グループ化するテキスト
    :return: グループ化したテキスト
    """

    modes = [char2mode(c) for c in text]
    if len(modes) == 0:
        return GroupedText()

    # 下のループのために番兵を仕込む
    modes += [...]
    text += '$'

    # モードが連続する箇所をまとめる
    result = GroupedText()
    prev = ModeText(modes[0], text[0])
    for mode, char in zip(modes[1:], text[1:]):
        if mode == prev.mode:
            prev.text += char
        else:
            result.append(prev)
            prev = ModeText(mode, char)
    return result


def list2str(lst: Iterable):
    """リストを文字列に変換する"""
    return '[' + ', '.join((str(x) for x in lst)) + ']'
