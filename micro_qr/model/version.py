from enum import Enum

from micro_qr.binary import bin2arr, BinaryArray


class Version(Enum):
    """
    型番

    P14 (PDF 17) 図11
    """

    M1 = (11, bin2arr(0, 3), 0)
    M2 = (13, bin2arr(0, 5), 1)
    M3 = (15, bin2arr(0, 7), 2)
    M4 = (17, bin2arr(0, 9), 3)

    def __init__(self, size: int, terminator: BinaryArray, mode_indicator_length: int):
        self.size = size
        """
        マイクロQRコードの一辺あたりのモジュール数
        
        P17 (PDF 20) 表1
        """

        self.terminator = terminator
        """
        終端パターン
        
        P30 (PDF 33) 7.4.9, P21 (PDF24) 表2 等
        """

        self.mode_indicator_length = mode_indicator_length
        """
        モード指示子の長さ
        
        P21 (PDF24) 表2 等
        """
