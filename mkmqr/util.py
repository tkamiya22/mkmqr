from .model import InvalidPairError


class Case:
    """
    if-elif-elseの補助
    Python 3.10からはパターンマッチが使える
    """

    def __init__(self, target):
        """
        :param target: 指定条件
        """
        self.target = target
        """指定条件"""
        self._value = ...

    def when(self, condition, value):
        """
        :param condition: 条件
        :param value: 値
        """
        if value is ...:
            raise ValueError(f'... is not supported')
        if self.target == condition:
            self._value = value
        return self

    @property
    def value(self):
        """条件にマッチした値"""
        if self._value is ...:
            raise InvalidPairError(f'Invalid value ({self.target})')
        return self._value
