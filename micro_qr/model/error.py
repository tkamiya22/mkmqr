"""
組み込み例外を詳細に分類するためのファイル
"""


class InvalidPairError(ValueError):
    """不正な組み合わせ"""
    def __init__(self, *args):
        super().__init__(*args)


class InvalidCharacterError(ValueError):
    """不正な文字"""
    def __init__(self, *args):
        super().__init__(*args)


class OverCapacityError(ValueError):
    """容量オーバー"""
    def __init__(self, *args):
        super().__init__(*args)
