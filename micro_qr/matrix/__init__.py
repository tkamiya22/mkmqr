"""
シンボルを構成する各パーツを作成する内部モジュール
"""

# 各パーツの生成
from .matrix_codeword import (
    # データコード語
    add_terminator,
    add_padding_bit,
    add_padding_codeword,
    segment2data_codeword,
    # 誤り訂正コード語
    get_generator_polynomial,
    setup_rs_code,
    get_error_correction_codeword,
    # 行列
    place_codeword,
    segment2matrix,
)
from .matrix_format_information import (
    place_format_information,
    get_format_information_matrix,
)
from .matrix_mask import (
    get_mask_matrix,
    calc_mask_score,
    get_optimal_mask,
)
from .matrix_function_pattern import (
    get_function_pattern_matrix,
)
