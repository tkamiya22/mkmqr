"""
マイクロQRコードを作成するライブラリ

参考：
`QRコードドットコム <https://www.qrcode.com/codes/microqr.html>`_
`JIS X0510 <https://www.jisc.go.jp/app/jis/general/GnrJISNumberNameSearchList?show&jisStdNo=X0510>`_
"""

from .binary import (
    BinaryArray,
    BinaryMatrix,
    arr2str,
    mat2str,
    arr2bin,
    bin2arr,
    bin2mat,
    concat_arr,
    merge_matrix,
    toggle_matrix,
    empty_matrix,
)

# from .error_correction import ()

from .model import (
    Version,
    Mode,
    ErrorCorrectionLevel,
    Mask,
    values,
    set_encoding,
    InvalidPairError,
    InvalidCharacterError,
    OverCapacityError,
)

from .matrix import (
    segment2matrix,
    get_format_information_matrix,
    get_optimal_mask,
    get_function_pattern_matrix,
)

from .factory import (
    data2segment,
    text2segment,
    add_quiet_zone,
    segment2symbol_matrix,
    symbol_matrix2image,
    create_symbol_matrix,
    create_symbol_image,
)

from .optimization import (
    analyze_text,
)
