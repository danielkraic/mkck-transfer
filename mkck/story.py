from typing import List

from mkck.debug import debug
from mkck.errors import EventError
from mkck.utils import clean_html


def get_event_story(file: str) -> str:
    with open(file, 'r') as f:
        event_story = clean_html(f.read())
        lines = [line.strip() for line in event_story.splitlines()]
        lines = [line for line in lines if line not in ['', '.']]

        header_index = _get_header_index(lines)
        footer_index = _get_footer_index(lines)

        debug('hd: {}'.format(header_index))
        debug('ft: {}'.format(footer_index))
        for i, line in enumerate(lines[header_index:footer_index]):
            debug('{}: {}'.format(i, line))

        valid_lines = lines[header_index:footer_index]
        if len(valid_lines) == 0:
            raise EventError('Event story from file {} is empty'.format(file))

        return '\n'.join(valid_lines)


def _get_header_index(lines: List[str]) -> int:
    index = 0
    for i, line in enumerate(lines):
        if index == 0:
            if line.startswith('Archív akcií'):
                index = i+1
        else:
            if line in ['', '<!--', 'pata', '//-->']:  # or line.startswith('Zápis z akcie'):
                index = i+1
            else:
                break

    return index


def _get_footer_index(lines: List[str]) -> int:
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

    for i, line in reversed(list(enumerate(lines))):
        if line.startswith('Foto z akcie:'):
            index = i
            break

    return index
