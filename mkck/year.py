import html
from os.path import exists
import re
from typing import List

from mkck.event import Event
from mkck.config import DIR_DOCS_BASE, FILE_YEAR, EVENTS_TO_SKIP_PER_YEAR
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
    with open(file, 'r') as f:
        return _get_events(year=year, content=f.read())


def _get_events(year: int, content: str) -> List[Event]:
    result = []

    # process all links
    links = re.findall(r'<a href.*akciadet.*cakcie=(\d+)[^>]*>([^<]+)<', content)
    for link in links:
        num, title = link
        title = html.unescape(title)
        title = title.replace(u'\xa0', u' ')

        if _skip_event(year=year, event_number=int(num)):
            continue

        event = Event(year=year, number=int(num), title=title, _date=extract_date(year=year, text=title))
        result.append(event)

    # process links for KT
    links = re.findall(r'<a href.*akciadet.*cakcie=KT[^>]*>([^<]+)<', content)
    for link in links:
        num, title = 99, link
        title = html.unescape(title)
        title = title.replace(u'\xa0', u' ')

        event = Event(year=year, number=int(num), title=title, _date=extract_date(year=year, text=title))
        result.append(event)

    # process links for non-planned events
    links = re.findall(r'akciadet.*rok=2per.*cakcie=([^"&]+)[^>]*>([^<]+)<', content)
    for i, link in enumerate(links):
        path, title = link
        num = 100 + i
        title = html.unescape(title)
        title = title.replace(u'\xa0', u' ')

        event = Event(year=year, number=num, title=title, _date=extract_date(year=year, text=title), planned=False,
                      path=path)
        result.append(event)

    return sorted(result, key=lambda item: item.date)


def _skip_event(year: int, event_number: int) -> bool:
    return event_number in EVENTS_TO_SKIP_PER_YEAR.get(year, [])
