"""
総当たりの実装が正しいと仮定し、山登り法について次の点を確認する

* 例外が発生しないこと
* 総当たりと同じ品質の解が出ること

グループの結合についての知見

* P94 (PDF 97)の附属書J「ビット列の長さの最適化」は任意のテキストを扱うには不十分 (扱っているのは隣接する2つのモードについてのみ)
* (A:ABC)(N:123)(A:DEF)のような同じモードに挟まれているパターンは、結合することでモード変更のためのオーバーヘッドが2箇所で消える
* 漢字モードを漢字モード以外と結合すると相手を巻き込んで8ビットバイトモードになるため、相手側の更に隣のグループと結合するする可能性がある
* ほとんどの場合、漢字モードとそれ以外のモードを結合するとビット長は悪化する

懸念事項
同じモードの文字が連続していたら、1つのモードに結合した方が良い という貪欲法でも用いているヒューリスティックが正しいか未確認
aaaa11111AAAAみたいなパターンにおいて、2つに切ってそれぞれ結合するみたいな方法も考えられなくはない
"""

import itertools
import unittest

from mkmqr import Version
from mkmqr.optimization.algorithm.opt_brute_force import optimize_brute_force
from mkmqr.optimization.algorithm.opt_hill_climbing import optimize_hill_climbing


class TestOptimization(unittest.TestCase):
    def is_equals_to_brute_force(self, version: Version, text: str):
        bf = optimize_brute_force(version, text)
        bf_len = bf.get_segment_length(version)

        with self.subTest(f'{version} {text} - hill climbing'):
            ct = optimize_hill_climbing(version, text)
            ct_len = ct.get_segment_length(version)
            self.assertEqual(bf_len, ct_len)

    def two_modes(self, version: Version, cl: str, ch: str, n_max: int):
        # テストの設定が妥当か？
        # nが小さいうちは結合した方(len(...)==1)が得であり、nが大きくなると分けた方が得となる
        # また、両側に挟まれているケースの方が、分けた方が得となるnの値が大きくなる
        # よって、両側に挟まれているケースについて、分けた方が得となるパターンが含まれているのか確認する
        bf = optimize_brute_force(version, ch + cl * n_max + ch)
        self.assertGreater(len(bf), 1, 'n_max is too small')

        for n in range(1, n_max+1):
            self.is_equals_to_brute_force(version, cl * n + ch)
        for n in range(1, n_max+1):
            self.is_equals_to_brute_force(version, ch + cl * n)
        for n in range(1, n_max+1):
            self.is_equals_to_brute_force(version, ch + cl * n + ch)

    def test_v1(self):
        self.is_equals_to_brute_force(Version.M1, '11111')

    def test_v2(self):
        self.two_modes(Version.M2, '1', 'A', 5)

    def test_v3(self):
        self.two_modes(Version.M3, '1', 'A', 7)
        self.two_modes(Version.M3, '1', 'a', 7)
        self.two_modes(Version.M3, 'A', 'a', 7)

    def test_v4(self):
        self.two_modes(Version.M4, '1', 'A', 10)
        self.two_modes(Version.M4, '1', 'a', 10)
        self.two_modes(Version.M4, 'A', 'a', 10)

    def test_kanji(self):
        # todo test_v*のような単純なケースでは、結合することで悪化することをテストで確認する
        for lo, li, ri, ro in itertools.product(['1', 'A', 'a'], repeat=4):
            self.is_equals_to_brute_force(Version.M4, f'{lo}{li}あ{ri}{ro}')
            self.is_equals_to_brute_force(Version.M4, f'{lo}{li}ああ{ri}{ro}')

    def test_kanji_ex(self):
        # todo エッジケースを理論的に攻める
        self.is_equals_to_brute_force(Version.M4, 'a11あAAa')
        self.is_equals_to_brute_force(Version.M4, '1AあA1AAあA1')

        self.is_equals_to_brute_force(Version.M4, '1AああA1AあA1')
        self.is_equals_to_brute_force(Version.M4, '1AあA1AああA1')

        self.is_equals_to_brute_force(Version.M4, '12月31日(火)')
        self.is_equals_to_brute_force(Version.M4, '1あ1a1あ1')


if __name__ == '__main__':
    unittest.main()
