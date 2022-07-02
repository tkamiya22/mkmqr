from enum import Enum


class ErrorCorrectionLevel(Enum):
    """
    誤り訂正レベル

    P34 (PDF 37) 7.5
    """

    NONE = 0
    """誤り検出のみ"""

    L = 1
    """復元能力 約7%"""

    M = 2
    """復元能力 約15%"""

    Q = 3
    """復元能力 約25%"""

    # マイクロQRコードでは使用できないので除外
    # H = 4
    # """復元能力 約30%"""
