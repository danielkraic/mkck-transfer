from datetime import date
from os.path import isdir, exists
from typing import Tuple, List, Optional


from mkck.config import EVENTS_WITHOUT_PHOTOS_PER_YEAR, DIR_PHOTOS, FILE_PHOTOS, FILE_STORY, DIR_DOCS_BASE
from mkck.errors import EventError
from mkck.gallery import GalleryItem
from mkck.photos import get_photos
from mkck.utils import extract_date
from mkck.story import get_event_story


def is_without_photos(year: int, number: int) -> bool:
    return number in EVENTS_WITHOUT_PHOTOS_PER_YEAR.get(year, [])


class Event(object):
    def __init__(self, year: int, number: int, title: str, _date: Optional[date]) -> None:
        self._year: int = year
        self._number: int = number
        self._is_planned = True  # TODO: add support for non-planned events
        self.title: str = title
        self.date: Optional[date] = _date
        self._story: str = self._get_story()
        self.photos: List[GalleryItem] = self._get_photos()

        if not self.date:
            self.date = extract_date(year=self._year, text=self._story)
            if not self.date:
                raise EventError('Failed to get date from event "{}"'.format(self))

        self._validate()

    @property
    def year(self) -> int:
        return self._year

    @property
    def event_number(self) -> int:
        return self._number

    @property
    def is_planned(self) -> bool:
        return self._is_planned

    def __str__(self):
        return '{}:{} t:{} d:{} c:{} p:{}'.format(self._year, self._number, self.title, self.date, len(self._story),
                                                  len(self.photos))

    def get_content(self, images: Optional[List[int]]=None) -> str:
        if not images:
            return self._get_story_content()

        return self._get_story_content() + '\n' + _get_gallery_content(images=images)

    def _get_story_content(self) -> str:
        lines = self._story.splitlines()
        if not lines:
            return ''

        if lines[0].startswith('Zápis z'):
            lines.pop(0)

        return '\n'.join(_format_lines(lines=lines))

    def _validate(self) -> None:
        try:
            if self._year < 1990:
                raise ValueError('Invalid event year {}'.format(self._year))

            if self._number < 1 or self._number > 50:
                raise ValueError('Invalid event number {}'.format(self._number))

            if len(self.title) < 3:
                raise ValueError('Invalid event title {}'.format(self.title))

            if len(self._story.splitlines()) < 2:
                raise ValueError('Invalid event story. Num of lines {}'.format(len(self._story.splitlines())))

            if len(self.photos) == 0 and not is_without_photos(year=self._year, number=self._number):
                raise ValueError('Invalid event photos. Num of photos {}'.format(len(self.photos)))

        except ValueError as error:
            raise EventError('Validation failed. Data: {}. Error: {}'.format(self.__str__(), error))

    def _get_story(self) -> str:
        story_file = self._get_event_story_path()

        if not exists(story_file):
            raise EventError('Event story file {} not exist'.format(story_file))

        return get_event_story(file=story_file)

    def _get_photos(self) -> List[GalleryItem]:
        photos_file, photos_dir = self._get_event_photos_paths()

        if not exists(photos_file):
            raise EventError('Event photos file {} not exist'.format(photos_file))

        if not exists(photos_dir) or not isdir(photos_dir):
            raise EventError('Invalid event photos dir {}'.format(photos_dir))

        photos_with_desc = get_photos(photos_file=photos_file, photos_dir=photos_dir)

        return [GalleryItem(year=self._year,
                            event_number=self._number,
                            image_number=i+1,
                            path=item.path,
                            caption=item.desc,
                            is_planned=self._is_planned)
                for i, item in enumerate(photos_with_desc)]

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


def _get_gallery_content(images: List[int]) -> str:
    images_str = ','.join([str(img) for img in images])
    return '[gallery columns="1" size="full" link="none" ids="{}"]'.format(images_str)


def _format_lines(lines: List[str]) -> List[str]:
    res = []

    for i, line in enumerate(lines):
        is_paragraph = _is_paragraph(line=line) and (i == 0 or _is_paragraph(line=lines[i - 1]))
        res.append(_format_line(line=line, is_paragraph=is_paragraph))

    return res


def _is_paragraph(line: str) -> bool:
    return not (line.startswith('·') or line.startswith('–') or line.endswith(':'))


def _format_line(line: str, is_paragraph: bool) -> str:
    if not is_paragraph:
        return line
    return '<p>{}</p>'.format(line)
