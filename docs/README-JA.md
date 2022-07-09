# mkmqr (MaKe Micro QR code)

マイクロQRコードを作成するライブラリです。  


## 特徴

* テキストを高い効率で符号化するため、シンボルの容量を最大限に活かすことができます
* テキストから最適な型番を自動的に選択します
* 選択した型番の中で誤り訂正レベルを最大化します


## デモ

| コマンド                                               |                                                           生成画像                                                           |
|:---------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------:|
| `python -m mkmqr 12345`                            | !["12345"を符号化したシンボル](https://raw.githubusercontent.com/tkamiya22/mkmqr/release/0.6.0/docs/img_ja/12345.png "マイクロQRコード")  |
| `python -m mkmqr -p 漢字.png 漢字もOK`                  |   !["漢字もOK"を符号化したシンボル](https://raw.githubusercontent.com/tkamiya22/mkmqr/release/0.6.0/docs/img_ja/漢字.png "マイクロQRコード")   |
| `python -m mkmqr -p Q.png -e q レベルQ`               |    !["レベルQ"を符号化したシンボル](https://raw.githubusercontent.com/tkamiya22/mkmqr/release/0.6.0/docs/img_ja/Q.png "マイクロQRコード")    |
| `python -m mkmqr -p github.png HTTPS://GITHUB.COM` | ![GitHubのURLを符号化したシンボル](https://raw.githubusercontent.com/tkamiya22/mkmqr/release/0.6.0/docs/img/github.png "マイクロQRコード") |

注意：マイクロQRコードを読み取る時には、URLが正しいか確認するなど、セキュリティに注意してください。


## 使い方

### コマンドラインから

テキストと誤り訂正レベル(任意)からマイクロQRコードを作成します。

引数の説明

|             |      引数      |                 候補                  |     デフォルト      |
|------------:|:------------:|:-----------------------------------:|:--------------:|
|  必要な誤り訂正レベル |     `-e`     | `x`(誤り検出のみ), `l`(L), `m`(M), `q`(Q) |      `x`       |
|   画像を保存するパス |     `-p`     |                  -                  | `./(テキスト).png` |
|     画像を表示する |     `-s`     |                `-s`                 |       なし       | 
| エンコーディングを指定 | `--encoding` |                  -                  |   shift-jis    |
|   デバッグ情報を表示 |     `-d`     |        `-d`, `-dd`(更に詳細を表示)         |       なし       |

### プログラムから

```python
from mkmqr import (
    ErrorCorrectionLevel, create_symbol_image,
    InvalidCharacterError, InvalidPairError, OverCapacityError
)

try:
    image = create_symbol_image('デモ', ErrorCorrectionLevel.M)
    image.show()
except OverCapacityError:
    print('容量を超えています。')
except InvalidCharacterError:
    # デフォルトでは最終的にShift-JISで符号化されます。
    print('符号化できない文字が使用されています。')
except InvalidPairError:
    # 自動識別を使用せずに型番などを指定した場合に投げられる可能性があります。
    print('型番や誤り訂正レベルの組み合わせが不正です。')
```


## インストール方法

* GitHub: `pip install git+https://github.com/tkamiya22/mkmqr.git`
* PyPI: `pip install mkmqr`


## 依存関係

* [numpy](https://github.com/numpy/numpy) >= 1.20.0
* [Pillow](https://github.com/python-pillow/Pillow) >= 9.1.0


## 備考

マイクロQRコードの概要については[QRコードドットコム](https://www.qrcode.com/codes/microqr.html)に掲載されています。  
また、詳細な仕様については[JIX X0510](https://www.jisc.go.jp/app/jis/general/GnrJISNumberNameSearchList?show&jisStdNo=X0510)に掲載されています。  

動作確認は[クルクル](https://www.qrqrq.com/)で行っています。  

QRコードは(株)デンソーウェーブの登録商標です。  


## 作者

神谷 俊樹
 

## ライセンス

MIT ライセンス
