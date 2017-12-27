from datetime import date
import fnmatch
import html
import os
from os.path import isdir, exists
import re
from typing import List, Tuple, Dict, Optional

from bs4 import BeautifulSoup, Tag

AKCIE_BASE = 'http://mkck.sk/akciezoz.php?rok='
DOCS_BASE = '/Users/danielkraic/work/code/web/mkck-old/unger/web/documents/akcie'
AKCIE_MIMO_BASE = '/Users/danielkraic/work/code/web/mkck-old/unger/web/documents/akcie/2per/'

YEAR_FILE = 'akciear.htm.txt'
CONTENT_FILE = 'zapis.htm.txt'
PHOTOS_FILE = 'foto.htm.txt'
PHOTOS_DIR = 'fot'

DEBUG = True

without_photos = {
    2015: [19]
}


def is_without_photos(year: int, number: int) -> bool:
    return number in without_photos.get(year, [])


def debug(message: str) -> None:
    if DEBUG:
        print(message)


class AkciaError(Exception):
    pass


class Akcia(object):
    def __init__(self, year: int, number: int, title: str, _date: Optional[date]):
        self._year: int = year
        self._number: int = number
        self._title: str = title
        self._date: Optional[date] = _date
        self._content: str = self._get_content()
        self._photos: Dict[str, str] = self._get_photos()

        if not self._date:
            self._date = _extract_date(year=self._year, text=self._content)

        self._validate()

    def __str__(self):
        return '{}:{} t:{} d:{} c:{} p:{}'.format(self._year, self._number, self._title, self._date, len(self._content),
                                                  len(self._photos))

    def _validate(self):
        try:
            if self._year < 1990:
                raise ValueError('Invalid year {}'.format(self._year))

            if self._number < 1 or self._number > 30:
                raise ValueError('Invalid number {}'.format(self._number))

            if len(self._title) < 3:
                raise ValueError('Invalid title {}'.format(self._title))

            if len(self._content.splitlines()) < 2:
                raise ValueError('Invalid content. Num of lines {}'.format(len(self._content.splitlines())))

            if len(self._photos.keys()) < 1 and not is_without_photos(year=self._year, number=self._number):
                raise ValueError('Invalid photos. Num of photos {}'.format(len(self._photos.keys())))
        except ValueError as error:
            raise AkciaError('Validation failed. Data: {}. Error: {}'.format(self.__str__(), error))

    def _get_content(self) -> str:
        content = self._get_akcia_content_path()

        if not exists(content):
            raise AkciaError('content {} not exist'.format(content))

        return _get_akcia_zapis(file=content)

    def _get_photos(self) -> Dict[str, str]:
        photos, photos_dir = self._get_akcia_photos_paths()

        if not exists(photos):
            raise AkciaError('photos {} not exist'.format(photos))

        if not exists(photos_dir) or not isdir(photos_dir):
            raise AkciaError('photos dir {} not exist'.format(photos_dir))

        photos_with_desc = _get_akcia_photos(file=photos)

        photo_files_all = _find_files(which='*.jpg', where=photos_dir)
        photo_files_fn = _find_files(which='*_tn.jpg', where=photos_dir)
        photo_files = {p.split('/')[-1]: p for p in photo_files_all if p not in photo_files_fn}

        return {photo_files.get(p): desc for p, desc in photos_with_desc.items()}

    def _get_akcia_base_path(self) -> str:
        return '{}/{}/{}/'.format(DOCS_BASE, self._year, self._number)

    def _get_akcia_content_path(self) -> str:
        return self._get_akcia_base_path() + CONTENT_FILE

    def _get_akcia_photos_paths(self) -> Tuple[str, str]:
        akcia_base = self._get_akcia_base_path()

        photos = akcia_base + PHOTOS_FILE
        photos_dir = akcia_base + PHOTOS_DIR
        if self._year >= 2015:
            photos_dir = akcia_base

        return photos, photos_dir


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

            akcia = Akcia(year=year, number=int(num), title=title, _date=_extract_date(year=year, text=title))
            result.append(akcia)

    return sorted(result, key=lambda item: '{:02d}'.format(item._number))


def _find_files(which: str, where: str='.') -> List[str]:
    rule = re.compile(fnmatch.translate(which), re.IGNORECASE)
    return [name for name in os.listdir(where) if rule.match(name)]


def _extract_date(year: int, text: str) -> Optional[date]:
    m = re.search(r'(\d{1,2})\.(\d{1,2})', text)
    if m:
        day = int(m.group(1))
        month = int(m.group(2))
        return date(year, month, day)

    return None


def _get_akcia_zapis(file: str) -> str:
    with open(file, 'r') as f:
        zapis = _clean_html(f.read())
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


def _get_akcia_photos(file: str) -> Dict[str, str]:
    imgs = {}

    with open(file, 'r') as f:
        last_img = None
        soup = BeautifulSoup(f.read(), 'html.parser')

        for sibling in soup.p.next_siblings:
            if not isinstance(sibling, Tag):
                continue

            img = _get_img(sibling)
            if img:
                if last_img:
                    imgs[last_img] = ''

                last_img = img.split('/')[-1]
            else:
                description = str(sibling.text).replace(u'\xa0', u' ').strip()
                if description and description != '':
                    if last_img:
                        imgs[last_img] = description
                        # debug('img: {} {}'.format(last_img, description))
                        last_img = None

    if last_img:
        imgs[last_img] = ''
        # debug('img: {}'.format(last_img))

    return imgs


def _get_img(element) -> Optional[str]:
    imgs = element.find_all('img')
    for img in imgs:
        src = img['src']
        if not src:
            return None

        return src

    return None


def _clean_html(raw_html: str) -> str:
    re_tags = re.compile(r'<.*?>')
    re_comments = re.compile(r'<!--.*?-->', flags=re.MULTILINE)
    re_nbsp = re.compile(r'&nbsp;')
    re_empty_line = re.compile(r'\n\s*\n', flags=re.MULTILINE)

    if len(raw_html.splitlines()) == 1:
        raw_html = raw_html.replace('div>', 'div>\n')

    raw_html = html.unescape(raw_html)
    text = re.sub(re_tags, '', raw_html)
    text = re.sub(re_nbsp, '', text)
    text = re.sub(re_comments, '', text)
    text = re.sub(re_empty_line, '\n\n', text)

    return text


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
