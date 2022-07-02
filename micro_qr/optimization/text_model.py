from typing import Optional, Protocol, List, Generic, TypeVar

from ..binary import bin2arr, concat_arr, BinaryArray
from ..factory import text2segment
from ..model import Mode, Version, values


def mode2char(mode: Optional[Mode]) -> str:  # todo 設置場所を考える
    """
    各モードを1文字で表す

    :param mode: モード
    :return: 半角1文字
    """
    if mode == Mode.Numeric:
        return 'N'
    elif mode == Mode.AlphaNumeric:
        return 'A'
    elif mode == Mode.EightBitByte:
        return '8'
    elif mode == Mode.Kanji:
        return 'K'
    else:
        return 'x'


class SupportsMode(Protocol):
    """モード取得可能"""

    @property
    def mode(self) -> Mode:
        return ...

    @property
    def text(self) -> str:
        return ...


class SupportsSegment(Protocol):
    """セグメント化可能"""

    def get_segment_length(self, version: Version) -> int:
        return ...

    def get_segment(self, version: Version) -> BinaryArray:
        return ...


class ModeText(SupportsSegment, SupportsMode):
    """モードが付与されたテキスト"""

    def __init__(self, mode: Mode, text: str):
        self._mode = mode
        """符号化のモード"""
        self._text = text
        """テキスト"""

    @property
    def mode(self) -> Mode:
        return self._mode

    @mode.setter
    def mode(self, value):
        self._mode = value

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value):
        self._text = value

    def __len__(self):
        return len(self.text)

    def __str__(self):
        c = mode2char(self.mode)
        return f'({c}:{self.text})'

    def __hash__(self):
        return hash((self.mode, self.text))

    def __eq__(self, other):
        if not isinstance(other, ModeText):
            return False
        return self.mode == other.mode and self.text == other.text

    def __deepcopy__(self, memo=...):
        return ModeText(self.mode, self.text)

    def get_segment_length(self, version: Version) -> int:
        mi_len = version.mode_indicator_length
        cci_len = values.get_character_count_indicator_length(version, self.mode)
        data_len = self.mode.bit_length(self.text)
        return mi_len + cci_len + data_len

    def get_segment(self, version: Version) -> BinaryArray:
        return text2segment(version, self.mode, self.text)


class SeparatedModeText(List[ModeText], SupportsSegment):
    """
    モードが付与されたテキスト
    内部的に複数のグループに分けられている
    """

    @property
    def mode(self) -> Optional[Mode]:
        modes = {item.mode for item in self}
        if Mode.EightBitByte in modes:
            return Mode.EightBitByte
        elif Mode.Kanji in modes:
            if len(modes - {Mode.Kanji}) > 0:
                return Mode.EightBitByte
            else:
                return Mode.Kanji
        elif Mode.AlphaNumeric in modes:
            return Mode.AlphaNumeric
        elif Mode.Numeric in modes:
            return Mode.Numeric
        else:
            return None  # len(...) == 0

    @property
    def text(self) -> str:
        return ''.join((sub_text.text for sub_text in self))

    def get_segment_length(self, version: Version) -> int:
        if len(self) == 0:
            return 0
        mi_len = version.mode_indicator_length
        cci_len = values.get_character_count_indicator_length(version, self.mode)
        data_len = self.mode.bit_length(self.text)
        return mi_len + cci_len + data_len

    def get_segment(self, version: Version) -> BinaryArray:
        if len(self) == 0:
            return bin2arr(0, 0)
        return text2segment(version, self.mode, self.text)

    def __str__(self) -> str:
        # x = ', '.join((str(sub_text) for sub_text in self))
        # return f'<{mode2char(self.mode)}:{x}>'
        return f'({mode2char(self.mode)}:{self.text})'

    def __getitem__(self, item):
        v = super().__getitem__(item)
        if isinstance(v, list):
            return SeparatedModeText(v)
        else:
            return v


T = TypeVar('T', bound=SupportsSegment)


class GroupedText(Generic[T], List[T], SupportsSegment):
    """セグメント化するグループに分けられたテキスト"""

    def get_segment_length(self, version: Version) -> int:
        return sum((item.get_segment_length(version) for item in self))

    def get_segment(self, version: Version) -> BinaryArray:
        return concat_arr([item.get_segment(version) for item in self])

    def __str__(self) -> str:
        x = ', '.join((str(item) for item in self))
        return f'[{x}]'

    def __getitem__(self, item):
        v = super().__getitem__(item)
        if isinstance(v, list):
            return GroupedText(v)
        else:
            return v
