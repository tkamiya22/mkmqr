# mkmqr (MaKe Micro QR code)

This is a package to make micro QR codes.  
[日本語版のREADMEはこちら](https://github.com/tkamiya22/mkmqr/blob/release/0.6.0/docs/README-JA.md)


## Features

* Efficient encoding of text, use the most of the capacity of the symbol
* Automatically selects the best model from the text
* Maximizes the error correction level with the selected model number


## DEMO

| command                                            |                                                              generated image                                                              |
|:---------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------:|
| `python -m mkmqr 12345`                            |    ![Symbol that encodes "12345"](https://raw.githubusercontent.com/tkamiya22/mkmqr/release/0.6.0/docs/img/12345.png "micro QR code")     |
| `python -m mkmqr -p kanji.png 漢字`                  |      ![Symbol that encodes "漢字"](https://raw.githubusercontent.com/tkamiya22/mkmqr/release/0.6.0/docs/img/kanji.png "micro QR code")      |
| `python -m mkmqr -p Q.png -e q LevelQ`             |      ![Symbol that encodes "LevelQ"](https://raw.githubusercontent.com/tkamiya22/mkmqr/release/0.6.0/docs/img/Q.png "micro QR code")      |
| `python -m mkmqr -p github.png HTTPS://GITHUB.COM` | ![Symbol that encodes URL of GitHub](https://raw.githubusercontent.com/tkamiya22/mkmqr/release/0.6.0/docs/img/github.png "micro QR code") |

Caution: When reading the micro QR code, please pay attention to security, for example, make sure the URL is correct.


## USAGE

### Command

Create a micro QR code from error correction level (optional) and text.

description of arguments

|                                 |   argument   |                      choice                       |    default     |
|--------------------------------:|:------------:|:-------------------------------------------------:|:--------------:|
| Required error correction level |     `-e`     | `x`(error detection only), `l`(L), `m`(M), `q`(Q) |      `x`       |
|          Path to save ths image |     `-p`     |                         -                         | `./(text).png` |
|                  Show the image |     `-s`     |                       `-s`                        |      none      | 
|                Specify encoding | `--encoding` |                         -                         |   shift-jis    |
|      Show debugging information |     `-d`     |           `-d`, `-dd`(more information)           |      none      |

### Program

```python
from mkmqr import (
    ErrorCorrectionLevel, create_symbol_image,
    InvalidCharacterError, InvalidPairError, OverCapacityError
)

try:
    image = create_symbol_image('demo', ErrorCorrectionLevel.M)
    image.show()
except OverCapacityError:
    print('Capacity is exceeded.')
except InvalidCharacterError:
    # By default, the final encoding is Shift-JIS.
    print('Unencodable characters are used.')
except InvalidPairError:
    # May be thrown if model number or other information is specified.
    print('The combination of the model or error correction level is incorrect.')
```


## Installation

* from GitHub: `pip install git+https://github.com/tkamiya22/mkmqr.git`
* from PyPI: `pip install mkmqr`


## Requirement

* [numpy](https://github.com/numpy/numpy) >= 1.20.0
* [Pillow](https://github.com/python-pillow/Pillow) >= 9.1.0


## Notes

An overview of Micro QR Code can be found at [QR code.com](https://www.qrcode.com/en/codes/microqr.html).  
The detailed specifications can be found at [JIX X0510](https://www.jisc.go.jp/app/jis/general/GnrJISNumberNameSearchList?show&jisStdNo=X0510).

The operation is confirmed by [QRQR](https://www.denso-wave.com/en/system/qr/product/reader.html).

QR Code is a registered trademark of DENSO WAVE INCORPORATED.


## Author
 
Toshiki Kamiya


## License

MIT license
