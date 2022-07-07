"""
多項式環を剰余体として扱うためのクラス
"""

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
        return (left + right) % self.primitive_polynomial

    def sub(self, left: PolynomialRing, right: PolynomialRing) -> PolynomialRing:
        return (left - right) % self.primitive_polynomial

    def mul(self, left: PolynomialRing, right: PolynomialRing) -> PolynomialRing:
        return (left * right) % self.primitive_polynomial

    def div(self, left: PolynomialRing, right: PolynomialRing) -> PolynomialRing:
        return (left / right) % self.primitive_polynomial

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
