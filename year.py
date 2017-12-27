import html
from os.path import exists
import re
from typing import List

from akcia import Akcia
from config import DOCS_BASE, YEAR_FILE
from errors import AkciaError
from utils import extract_date


def get_year_list(year: int) -> List[Akcia]:
    year_file = _get_year_file_path(year)
    if not exists(year_file):
        raise AkciaError('File {} not exist'.format(year_file))

    return _read_year_file(year=year, file=year_file)


def _get_year_file_path(year: int) -> str:
    return '{}/{}/{}'.format(DOCS_BASE, year, YEAR_FILE)


def _read_year_file(year: int, file: str) -> List[Akcia]:
    result = []

    with open(file, 'r') as f:
        content = f.read()
        links = re.findall(r'<a href.*akciadet.*cakcie=(\d+).*>(.*)<\/a>', content)

        for link in links:
            num, title = link
            title = html.unescape(title)
            title = title.replace(u'\xa0', u' ')

            akcia = Akcia(year=year, number=int(num), title=title, _date=extract_date(year=year, text=title))
            result.append(akcia)

    return sorted(result, key=lambda item: '{:02d}'.format(item._number))
