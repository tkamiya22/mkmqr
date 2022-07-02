"""
RS符号を計算するためのファイル
"""

from .polynomial_ring import PolynomialRing
from .residue_field import ResidueFieldOperator
from typing import List, Union


class ReedSolomonCode:
    """RS符号を計算するクラス"""

    def __init__(
            self,
            primitive_polynomial: Union[PolynomialRing, ResidueFieldOperator],
            generator_polynomial: List[PolynomialRing]
    ):
        """
        :param primitive_polynomial: 原始多項式
        :param generator_polynomial: 生成多項式 (高次 gp[0] ← ... → gp[-1] 低次)
        """
        if isinstance(primitive_polynomial, PolynomialRing):
            rf_op = ResidueFieldOperator(primitive_polynomial)
        else:
            rf_op = primitive_polynomial

        self.rf_op = rf_op
        """剰余体の計算補助"""
        self.generator_polynomial = generator_polynomial
        """生成多項式"""

    @property
    def primitive_polynomial(self):
        """原始多項式"""
        return self.rf_op.primitive_polynomial

    def encode(self, data: List[PolynomialRing]) -> List[PolynomialRing]:
        """
        符号化を行う (計算前に自動で桁をシフトする)

        :param data: RS符号を求めるデータ
        :return: 求めたRS符号
        """
        n = len(self.generator_polynomial) - 1
        trail = [PolynomialRing(0) for _ in range(n)]
        return self.encode_raw(data + trail)

    def encode_raw(self, data: List[PolynomialRing]) -> List[PolynomialRing]:
        """
        符号化を行う (計算前に桁をシフトしない)

        :param data: RS符号を求めるデータ
        :return: 求めたRS符号
        """
        temp = data.copy()

        # 筆算のように最高次から順番に引いていく
        for i in range(len(temp) - len(self.generator_polynomial) + 1):
            # 商を求める (最高次は1のはずだが、一応割る)
            q = temp[i] / self.generator_polynomial[0]
            for j in range(len(self.generator_polynomial)):
                temp[i+j] = self.rf_op.sub(temp[i+j], q * self.generator_polynomial[j])

        # 剰余だけ取り出す
        return temp[-(len(self.generator_polynomial)-1):]
