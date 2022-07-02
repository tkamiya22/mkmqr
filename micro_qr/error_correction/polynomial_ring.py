"""
多項式環 F2[x]を扱うためのファイル
"""

from typing import *


F2Array = int  # bitarray
"""有限体F2の配列とみなすビット列"""


class PolynomialRing:
    """多項式環 F2[x]"""

    def __init__(self, coefficient: F2Array):
        """
        :param coefficient: 多項式の係数 (x^3 + x + 1 なら 0b1011)
        """
        if not isinstance(coefficient, F2Array):
            raise TypeError(f'coefficient must be int, but {type(coefficient)} was given')

        if coefficient < 0:
            raise ValueError('coefficient must be greater than or equal to 0')
        self._coefficient = coefficient

    @property
    def coefficient(self):
        return self._coefficient

    # region 演算
    def __add__(self, other: 'PolynomialRing') -> 'PolynomialRing':
        return PolynomialRing(self._coefficient ^ other._coefficient)

    def __sub__(self, other: 'PolynomialRing') -> 'PolynomialRing':
        return self + other

    def __mul__(self, other: 'PolynomialRing') -> 'PolynomialRing':
        left_cof = self._coefficient
        right_cof = other._coefficient

        # 筆算の要領で足し合わせていく
        result = 0
        while right_cof > 0:
            if right_cof & 1 == 1:  # 末尾の1桁に注目する
                result ^= left_cof  # 有限体F2の加算はビットのXORに相当
            right_cof >>= 1  # 処理した桁を破棄し、次の桁を末尾へ降ろす
            left_cof <<= 1  # 足し合わせるために位取りを合わせる

        return PolynomialRing(result)

    def __truediv__(self, other: 'PolynomialRing') -> 'PolynomialRing':
        return self.__divmod__(other)[0]

    def __mod__(self, other: 'PolynomialRing') -> 'PolynomialRing':
        return self.__divmod__(other)[1]

    def __divmod__(self, other: 'PolynomialRing') -> Tuple['PolynomialRing', 'PolynomialRing']:
        left_cof = self._coefficient
        right_cof = other._coefficient

        def bin_digit_num(n):
            """二進数の桁数を数える"""
            m = 0
            while n != 0:
                n >>= 1
                m += 1
            return m

        quotient = 0
        while True:
            shift_amount = bin_digit_num(left_cof) - bin_digit_num(right_cof)
            if shift_amount < 0:
                break
            left_cof ^= right_cof << shift_amount
            quotient ^= 1 << shift_amount

        return PolynomialRing(quotient), PolynomialRing(left_cof)
    # endregion

    def __hash__(self) -> int:
        return hash(self._coefficient)

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._coefficient == other._coefficient

    def __str__(self) -> str:
        return f'{self._coefficient:b}'

    def __repr__(self):
        return f'PolynomialRing({bin(self._coefficient)})'
