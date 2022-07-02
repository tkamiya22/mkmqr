"""
python -m miqro_qr
"""

import argparse
import sys
from logging import getLogger, StreamHandler, Formatter, DEBUG, INFO
from typing import Optional

import micro_qr
from .factory import create_symbol_image
from .model import ErrorCorrectionLevel as ECL, InvalidPairError, InvalidCharacterError, OverCapacityError, set_encoding

handler = StreamHandler()
# handler.setFormatter(Formatter('[{levelname:>8}] {filename:20} L{lineno:3}, {funcName:25} : {message}', style='{'))
handler.setFormatter(Formatter('%(message)s'))
logger = getLogger(micro_qr.__name__)
logger.addHandler(handler)


def main():
    # help_ecl = '誤り訂正レベル'
    # help_path = '画像を保存するパス'
    # help_encoding = 'エンコーディング (bビットバイトモードのみ)'
    # help_show = '画像を表示する'
    # help_debug = 'デバッグ情報を表示'
    # help_text = 'マイクロQRコードにするテキスト'
    help_ecl = 'required error correction level'
    help_path = 'path to save the image'
    help_encoding = 'encoding (8-bit byte mode only)'
    help_show = 'show the image'
    help_debug = 'show debug message'
    help_text = 'text to make micro QR code'

    ecls = {
        'x': ECL.NONE,
        'l': ECL.L,
        'm': ECL.M,
        'q': ECL.Q,
    }

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-e', '--ecl',
        choices=ecls.keys(), default='x', help=help_ecl
    )
    parser.add_argument(
        '-p', '--path',
        help=help_path
    )
    parser.add_argument(
        '--encoding',
        default='shift-jis',
        help=help_encoding
    )
    parser.add_argument(
        '-s', '--show',
        action='store_true',
        help=help_show
    )
    parser.add_argument(
        '-d', '--debug',
        action='count',
        help=help_debug
    )
    parser.add_argument(
        'text',
        help=help_text
    )

    args = parser.parse_args()
    ecl: ECL = ecls[args.ecl]
    path: Optional[str] = args.path
    encoding: str = args.encoding
    show: bool = args.show
    debug: Optional[int] = args.debug
    text: str = args.text

    if not show:
        if path is None:
            path = f'./{text}.png'
        elif path.endswith('/'):
            path = path + f'{text}.png'

    if debug:
        if debug == 1:
            level = INFO
        else:  # debug >= 2
            level = DEBUG
        logger.setLevel(level)
        handler.setLevel(level)

    try:
        logger.info(f'ecl:      {ecl}')
        logger.info(f'path:     {path}')
        logger.info(f'show:     {show}')
        logger.info(f'encoding: {encoding}')
        logger.info(f'debug:    {debug}')
        logger.info(f'text:     {text}')
        logger.info('------------------------------------')

        set_encoding(encoding)
        image = create_symbol_image(text, ecl)

        if path is not None:
            image.save(path)
            logger.info(f'image saved')
        if show:
            image.show(text)
    except OverCapacityError:
        print(f'over capacity', file=sys.stderr)
    except InvalidCharacterError as e:
        print(f'invalid character : {e.args[1]}', file=sys.stderr)
    except InvalidPairError:
        print(f'invalid pair', file=sys.stderr)


if __name__ == '__main__':
    main()
