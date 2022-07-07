"""
マイクロQRコードで使用されるモデルをまとめた内部モジュール
"""

from .version import Version
from .mode import Mode, set_encoding
from .error_correction_level import ErrorCorrectionLevel
from .mask import Mask

from .error import InvalidPairError, InvalidCharacterError, OverCapacityError

