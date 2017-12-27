import html
from os.path import exists
import re
from typing import List

from mkck.event import Event
from mkck.config import DIR_DOCS_BASE, FILE_YEAR
from mkck.errors import EventError
from mkck.utils import extract_date


def get_year_events_list(year: int) -> List[Event]:
    year_file = _get_year_file_path(year)
    if not exists(year_file):
        raise EventError('File {} not exist'.format(year_file))

    return _read_year_file(year=year, file=year_file)


def _get_year_file_path(year: int) -> str:
    return '{}/{}/{}'.format(DIR_DOCS_BASE, year, FILE_YEAR)


def _read_year_file(year: int, file: str) -> List[Event]:
    result = []

    with open(file, 'r') as f:
        content = f.read()
        links = re.findall(r'<a href.*akciadet.*cakcie=(\d+).*>(.*)<\/a>', content)

        for link in links:
            num, title = link
            title = html.unescape(title)
            title = title.replace(u'\xa0', u' ')

            event = Event(year=year, number=int(num), title=title, _date=extract_date(year=year, text=title))
            result.append(event)

    return sorted(result, key=lambda item: '{:02d}'.format(item._number))
