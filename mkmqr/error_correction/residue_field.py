"""
多項式環を剰余体として扱うためのクラス
"""
from typing import Tuple

from .polynomial_ring import PolynomialRing, F2Array


class ResidueFieldOperator:
    """多項式環を剰余体として扱うためのクラス"""

    def __init__(self, primitive_polynomial: PolynomialRing):
        """
        :param primitive_polynomial: 原始多項式
        """
        self.primitive_polynomial = primitive_polynomial
        """原始多項式"""

    def add(self, left: PolynomialRing, right: PolynomialRing) -> PolynomialRing:
        """
        加算

        :param left: 左オペランド
        :param right: 右オペランド
        :return: 和
        """
        return (left + right) % self.primitive_polynomial

    def sub(self, left: PolynomialRing, right: PolynomialRing) -> PolynomialRing:
        """
        減算

        :param left: 左オペランド
        :param right: 右オペランド
        :return: 差
        """
        return (left - right) % self.primitive_polynomial

    def mul(self, left: PolynomialRing, right: PolynomialRing) -> PolynomialRing:
        """
        乗算

        :param left: 左オペランド
        :param right: 右オペランド
        :return: 積
        """
        return (left * right) % self.primitive_polynomial

    def div(self, left: PolynomialRing, right: PolynomialRing) -> PolynomialRing:
        """
        除算

        :param left: 左オペランド
        :param right: 右オペランド
        :return: 商
        """
        return (left * self.inv(right)) % self.primitive_polynomial

    def inv(self, value: PolynomialRing) -> PolynomialRing:
        """
        逆元

        :param value: オペランド
        :return: 逆元
        """
        if value.coefficient == 0:
            raise ZeroDivisionError()
        _, (inv, _) = self._ext_gcd(value, self.primitive_polynomial)
        return inv

    @classmethod
    def _ext_gcd(cls, a: PolynomialRing, b: PolynomialRing) \
            -> Tuple[PolynomialRing, Tuple[PolynomialRing, PolynomialRing]]:
        """
        | 拡張ユークリッドの互除法
        | a*x + b*y == 1 となる (x, y)を求める

        :param a:
        :param b:
        :return: aとbの最大公約数, (x, y)
        """
        if b.coefficient == 0:
            return a, (PolynomialRing(1), PolynomialRing(0))
        d, (y, x) = cls._ext_gcd(b, a % b)
        y -= a/b * x
        return d, (x, y)

    def from_exp(self, exp: int):
        """
        べき表現から剰余体の元を取得する

        :param exp: べき表現
        :return: 対応する剰余体の元
        """
        return PolynomialRing(1 << exp) % self.primitive_polynomial

    def from_coefficient(self, coefficient: F2Array):
        """
        多項式表現から剰余体の元を取得する

        :param coefficient: 多項式表現
        :return: 対応する剰余体の元
        """
        return PolynomialRing(coefficient) % self.primitive_polynomial
