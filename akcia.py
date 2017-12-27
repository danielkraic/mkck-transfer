from datetime import date
from os.path import isdir, exists
from typing import Tuple, Dict, Optional


from config import without_photos, PHOTOS_DIR, PHOTOS_FILE, CONTENT_FILE, DOCS_BASE
from errors import AkciaError
from photos import get_akcia_photos
from utils import extract_date, find_files
from zapis import get_akcia_zapis


class Akcia(object):
    def __init__(self, year: int, number: int, title: str, _date: Optional[date]):
        self._year: int = year
        self._number: int = number
        self._title: str = title
        self._date: Optional[date] = _date
        self._content: str = self._get_content()
        self._photos: Dict[str, str] = self._get_photos()

        if not self._date:
            self._date = extract_date(year=self._year, text=self._content)

        self._validate()

    def __str__(self):
        return '{}:{} t:{} d:{} c:{} p:{}'.format(self._year, self._number, self._title, self._date, len(self._content),
                                                  len(self._photos))

    @staticmethod
    def is_without_photos(year: int, number: int) -> bool:
        return number in without_photos.get(year, [])

    def _validate(self):
        try:
            if self._year < 1990:
                raise ValueError('Invalid year {}'.format(self._year))

            if self._number < 1 or self._number > 50:
                raise ValueError('Invalid number {}'.format(self._number))

            if len(self._title) < 3:
                raise ValueError('Invalid title {}'.format(self._title))

            if len(self._content.splitlines()) < 2:
                raise ValueError('Invalid content. Num of lines {}'.format(len(self._content.splitlines())))

            if len(self._photos.keys()) < 1 and not Akcia.is_without_photos(year=self._year, number=self._number):
                raise ValueError('Invalid photos. Num of photos {}'.format(len(self._photos.keys())))
        except ValueError as error:
            raise AkciaError('Validation failed. Data: {}. Error: {}'.format(self.__str__(), error))

    def _get_content(self) -> str:
        content = self._get_akcia_content_path()

        if not exists(content):
            raise AkciaError('content {} not exist'.format(content))

        return get_akcia_zapis(file=content)

    def _get_photos(self) -> Dict[str, str]:
        photos, photos_dir = self._get_akcia_photos_paths()

        if not exists(photos):
            raise AkciaError('photos {} not exist'.format(photos))

        if not exists(photos_dir) or not isdir(photos_dir):
            raise AkciaError('photos dir {} not exist'.format(photos_dir))

        photos_with_desc = get_akcia_photos(file=photos)

        photo_files_all = find_files(which='*.jpg', where=photos_dir)
        photo_files_fn = find_files(which='*_tn.jpg', where=photos_dir)
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
