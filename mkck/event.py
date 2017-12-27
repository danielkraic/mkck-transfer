from datetime import date
from os.path import isdir, exists
from typing import Tuple, Dict, Optional


from mkck.config import events_per_year_without_photos, DIR_PHOTOS, FILE_PHOTOS, FILE_STORY, DIR_DOCS_BASE
from mkck.errors import EventError
from mkck.photos import get_event_photos
from mkck.utils import extract_date, find_files
from mkck.story import get_event_story


def is_without_photos(year: int, number: int) -> bool:
    return number in events_per_year_without_photos.get(year, [])


class Event(object):
    def __init__(self, year: int, number: int, title: str, _date: Optional[date]):
        self._year: int = year
        self._number: int = number
        self._title: str = title
        self._date: Optional[date] = _date
        self._story: str = self._get_story()
        self._photos: Dict[str, str] = self._get_photos()

        if not self._date:
            self._date = extract_date(year=self._year, text=self._story)

        self._validate()

    def __str__(self):
        return '{}:{} t:{} d:{} c:{} p:{}'.format(self._year, self._number, self._title, self._date, len(self._story),
                                                  len(self._photos))

    def _validate(self):
        try:
            if self._year < 1990:
                raise ValueError('Invalid event year {}'.format(self._year))

            if self._number < 1 or self._number > 50:
                raise ValueError('Invalid event number {}'.format(self._number))

            if len(self._title) < 3:
                raise ValueError('Invalid event title {}'.format(self._title))

            if len(self._story.splitlines()) < 2:
                raise ValueError('Invalid event story. Num of lines {}'.format(len(self._story.splitlines())))

            if len(self._photos.keys()) < 1 and not is_without_photos(year=self._year, number=self._number):
                raise ValueError('Invalid event photos. Num of photos {}'.format(len(self._photos.keys())))
        except ValueError as error:
            raise EventError('Validation failed. Data: {}. Error: {}'.format(self.__str__(), error))

    def _get_story(self) -> str:
        story_file = self._get_event_story_path()

        if not exists(story_file):
            raise EventError('Event story file {} not exist'.format(story_file))

        return get_event_story(file=story_file)

    def _get_photos(self) -> Dict[str, str]:
        photos_file, photos_dir = self._get_event_photos_paths()

        if not exists(photos_file):
            raise EventError('Event photos file {} not exist'.format(photos_file))

        if not exists(photos_dir) or not isdir(photos_dir):
            raise EventError('Invalid event photos dir {}'.format(photos_dir))

        photos_with_desc = get_event_photos(file=photos_file)

        photo_files_all = find_files(which='*.jpg', where=photos_dir)
        photo_files_fn = find_files(which='*_tn.jpg', where=photos_dir)
        photo_files = {p.split('/')[-1]: p for p in photo_files_all if p not in photo_files_fn}

        return {photo_files.get(p): desc for p, desc in photos_with_desc.items()}

    def _get_event_base_path(self) -> str:
        return '{}/{}/{}/'.format(DIR_DOCS_BASE, self._year, self._number)

    def _get_event_story_path(self) -> str:
        return self._get_event_base_path() + FILE_STORY

    def _get_event_photos_paths(self) -> Tuple[str, str]:
        event_base = self._get_event_base_path()

        photos_file = event_base + FILE_PHOTOS
        photos_dir = event_base + DIR_PHOTOS
        if self._year >= 2015:
            photos_dir = event_base

        return photos_file, photos_dir
