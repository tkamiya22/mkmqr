from enum import Enum
from typing import Callable
from mkmqr.binary import bin2arr, BinaryArray


class Mask(Enum):
    """
    マスク

    P49 (PDF 52) 7.8
    """

    Mask00 = (0, lambda y, x: y % 2 == 0)
    Mask01 = (1, lambda y, x: (y // 2 + x // 3) % 2 == 0)
    Mask10 = (2, lambda y, x: ((x * y) % 2 + (x * y) % 3) % 2 == 0)
    Mask11 = (3, lambda y, x: ((x + y) % 2 + (x * y) % 3) % 2 == 0)

    def __init__(self, mask_pattern_value: int, function: Callable[[int, int], bool]):
        self.mask_pattern_value = mask_pattern_value
        """
        マスクパターン参照子の値
        
        P49 (PDF 52) 表10
        """

        self.function = function
        """
        マスクする範囲を示す関数
        
        P49 (PDF 52) 表10
        """

    @property
    def mask_pattern_reference(self) -> BinaryArray:
        """
        マスクパターン参照子

        P49 (PDF 52) 表10
        """
        return bin2arr(self.mask_pattern_value, 2)
