"""
バイナリ形式のデータを使うための内部モジュール
"""

# それぞれの実体はnumpyのndarrayだが、隠蔽して使用する
# (numpyはこの内部モジュール以外ではimportしないようにする)

from .array import (
    BinaryArray,
    arr2bin,
    bin2arr,
    arr2str,
    concat_arr,
)
from .matrix import (
    BinaryMatrix,
    bin2mat,
    mat2str,
    merge_matrix,
    toggle_matrix,
    empty_matrix,
)
