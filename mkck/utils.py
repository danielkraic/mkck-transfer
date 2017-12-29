from datetime import date, datetime
import fnmatch
import html
import os
import re
from typing import List, Optional


def clean_html(raw_html: str) -> str:
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


def find_files(which: str, where: str='.') -> List[str]:
    rule = re.compile(fnmatch.translate(which), re.IGNORECASE)
    return [name for name in os.listdir(where) if rule.match(name)]


def extract_date(year: int, text: str) -> Optional[date]:
    m = re.search(r'(\d{1,2})\.(\d{1,2})', text)
    if m:
        day = int(m.group(1))
        month = int(m.group(2))
        return date(year, month, day)

    return None


def format_iso_date(iso_date: str) -> str:
    if not iso_date:
        return ''

    dt = datetime.strptime(iso_date, "%Y-%m-%dT%H:%M:%S")
    return ' ({}.{}.)'.format(dt.day, dt.month)
