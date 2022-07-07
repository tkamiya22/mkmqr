"""
テキストの符号化を行う各種モードについてのファイル
"""


from enum import Enum
from typing import List, Optional, Union

from ..binary import bin2arr, BinaryArray, concat_arr


def _each_slice(lst: str, n: int) -> List[str]:
    return [lst[i:i+n] for i in range(0, len(lst), n)]


class _NumericMode:
    """
    数字モード

    P23 (PDF 26) 7.4.3
    """

    def __init__(self):
        self.label = '数字モード'
        self.mode_indicator_value = 0

    def is_valid(self, text: str) -> bool:
        return all((c in '0123465789' for c in text))

    def encode(self, text: str) -> BinaryArray:
        def f(txt: str):
            txt2bin = {1: 4, 2: 7, 3: 10}
            txt_len = len(txt)
            bin_len = txt2bin[txt_len]
            return bin2arr(int(txt), bin_len)

        return concat_arr([f(txt) for txt in _each_slice(text, 3)])

    def bit_length(self, character_count: int) -> int:
        d = 10 * (character_count // 3)
        r = 0 if character_count % 3 == 0 else\
            4 if character_count % 3 == 1 else\
            7  # if character_count % 3 == 2
        return d + r

    def character_count(self, text: str) -> int:
        return len(text)


class _AlphaNumericMode:
    """
    英数字モード

    P24 (PDF 27) 7.4.4
    """

    def __init__(self):
        self.label = '英数字モード'
        self.mode_indicator_value = 1

        self._table = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:'

    def is_valid(self, text: str) -> bool:
        return all((c in self._table for c in text))

    def encode(self, text: str) -> BinaryArray:
        def f(txt: str):
            indices = [self._table.index(c) for c in txt]
            if len(indices) == 1:
                return bin2arr(indices[0], 6)
            else:  # len(indices) == 2
                return bin2arr(indices[0] * 45 + indices[1], 11)

        return concat_arr([f(txt) for txt in _each_slice(text, 2)])

    def bit_length(self, character_count: int) -> int:
        d = 11 * (character_count // 2)
        r = 6 * (character_count % 2)
        return d + r

    def character_count(self, text: str) -> int:
        return len(text)


class _EightBitByteMode:
    """
    8ビットバイトモード

    P25 (PDF 28) 7.4.5
    """

    def __init__(self):
        self.label = '8ビットバイトモード'
        self.mode_indicator_value = 2

        self.encoding = 'shift-jis'  # JIS X0510 P88(PDF 91)の附属書Hに掲載されたJIS X0201のスーパーセット
        # self.encoding = 'ISO_8859_1'  # JIS X0510 P26(PDF 29)に掲載された文字コード
        # self.encoding = 'utf-8'  # クルクルで読み取り可能

    def is_valid(self, text: str) -> bool:
        try:
            # b = text.encode(self._encoding)
            # return all((0x00 <= x <= 0x7F or 0xA0 <= x <= 0xDF for x in b))
            text.encode(self.encoding)
            return True
        except UnicodeError:
            return False

    def encode(self, text: str) -> BinaryArray:
        return concat_arr([bin2arr(b, 8) for b in text.encode(self.encoding)])

    def bit_length(self, character_count: int) -> int:
        return 8 * character_count
    
    def character_count(self, text: str) -> int:
        return len(text.encode(self.encoding))


class _KanjiMode:
    """
    漢字モード

    P27 (PDF 30) 7.4.6
    """

    def __init__(self):
        self.label = '漢字モード'
        self.mode_indicator_value = 3

        self._encoding = 'Shift-JIS'

    def is_valid(self, text: str) -> bool:
        def check(char: str):
            try:
                # return len(char.encode(self._encoding)) == 2
                x = int.from_bytes(char.encode(self._encoding), 'big')
                high, low = divmod(x, 0x100)
                return (0x8140 <= x <= 0x9FFC or 0xE040 <= x <= 0xEBBF) and low != 0x7F
            except UnicodeError:
                return False

        return all((check(c) for c in text))

    def encode(self, text: str) -> BinaryArray:
        def cvt(char: str):
            x = int.from_bytes(char.encode(self._encoding), 'big')
            if 0x8140 <= x <= 0x9FFC:
                x -= 0x8140
            else:  # elif 0xE040 <= x <= 0xEBBF:
                x -= 0xC140
            high, low = divmod(x, 0x100)
            x = 0xC0 * high + low
            return bin2arr(x, 13)

        return concat_arr([cvt(c) for c in text])

    def bit_length(self, character_count: int) -> int:
        return 13 * character_count
    
    def character_count(self, text: str) -> int:
        return len(text)


class Mode(Enum):
    """
    モード

    P18 (PDF 22) 7.3
    """

    Numeric = _NumericMode()
    """数字モード"""

    AlphaNumeric = _AlphaNumericMode()
    """英数字モード"""

    EightBitByte = _EightBitByteMode()
    """8ビットバイトモード"""

    Kanji = _KanjiMode()
    """漢字モード"""

    @property
    def label(self) -> str:
        """モードの名称"""
        return self.value.label

    @property
    def mode_indicator_value(self) -> int:
        """
        モード指示子の値

        P21 (PDF 24) 表2
        """
        return self.value.mode_indicator_value

    def is_valid(self, text: str) -> bool:
        """符号化可能か？"""
        return self.value.is_valid(text)

    def encode(self, text: str) -> Optional[BinaryArray]:
        """符号化を行う"""
        # if not self.value.is_valid(text):
        #     return None
        return self.value.encode(text)

    def character_count(self, text: str) -> int:
        """マルチバイト文字を考慮した文字数"""
        return self.value.character_count(text)

    def bit_length(self, text_or_character_count: Union[int, str]) -> int:
        """
        符号化後の2進データのビット数
        (実際に符号化できるかは考慮しない)

        :param text_or_character_count: テキストまたは文字数
        """
        # [memo]
        # 符号化の際に文字数指示子がOverCapacityErrorを投げる可能性がある
        # また、符号化ができてもシンボルの容量を超える可能性がある
        # そのため符号化→容量チェックの順に行うとtry-exceptとifの両方が必要となり、フローが複雑となる
        # これを防ぐためにデータ長を見積もるメソッドを用意し、先に容量チェックしてから符号化する
        # (容量を見積もることは文字数指示子が収まることの十分条件である はず)
        if isinstance(text_or_character_count, str):
            character_count = self.character_count(text_or_character_count)
        else:
            character_count = text_or_character_count
        return self.value.bit_length(character_count)


# FIXME そもそもEnumである必要はあるのかを含めて、設計を見直す (特に mode == Mode.Numeric のような判定に影響しないか？)
def set_encoding(encoding: str):
    """
    8ビットバイトモードのエンコーディングを指定する

    :param encoding: 文字エンコーディング
    """
    Mode.EightBitByte.value.encoding = encoding
