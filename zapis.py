from typing import List

from debug import debug
from errors import AkciaError
from utils import clean_html


def get_akcia_zapis(file: str) -> str:
    with open(file, 'r') as f:
        zapis = clean_html(f.read())
        lines = [line.strip() for line in zapis.splitlines()]
        lines = [line for line in lines if line != '']

        header_index = _get_zapis_header_index(lines)
        footer_index = _get_zapis_footer_index(lines)

        debug('hd: {}'.format(header_index))
        debug('ft: {}'.format(footer_index))
        for i, line in enumerate(lines[header_index:footer_index]):
            debug('{}: {}'.format(i, line))

        valid_lines = lines[header_index:footer_index]
        if len(valid_lines) == 0:
            raise AkciaError('Zapis from file {} is empty'.format(file))

        return '\n'.join(valid_lines)


def _get_zapis_header_index(lines: List[str]) -> int:
    index = 0
    for i, line in enumerate(lines):
        if index == 0:
            if line.startswith('Archív akcií'):
                index = i+1
        else:
            if line == '':
                index = i+1
            else:
                break

    return index


def _get_zapis_footer_index(lines: List[str]) -> int:
    index = -1
    for i, line in reversed(list(enumerate(lines))):
        # print('{}: {}'.format(i, line))
        if index == -1:
            if line.startswith('pata') or line.startswith('Stránka MKCK - Malo'):
                index = i
        else:
            if line in ['', '<!--', 'pata', '//-->']:
                index = i
            else:
                break

    return index
