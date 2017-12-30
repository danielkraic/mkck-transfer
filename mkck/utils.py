from datetime import date, datetime
import fnmatch
import html
import os
import re
from typing import List, Optional


def clean_html(raw_html: str) -> str:
    lines_count = len(raw_html.splitlines())
    if lines_count == 1:
        raw_html = raw_html.replace('div>', 'div>\n')
    if lines_count <= 5:
        raw_html = raw_html.replace('<p>', '\n<p>')

    lines = raw_html.splitlines()
    tag_if = None
    tag_endif = None
    for i, line in enumerate(lines):
        if not tag_if and line.find('[if gte ') != -1:
            tag_if = i
        if line.find('<![endif]') != -1:
            tag_endif = i

    if tag_if and tag_endif:
        raw_html = '\n'.join(lines[0:tag_if] + lines[tag_endif+1:])

    re_nbsp = re.compile(r'&nbsp;')
    re_ndash = re.compile(r'&ndash;')
    raw_html = re.sub(re_nbsp, ' ', raw_html)
    raw_html = re.sub(re_ndash, ' ', raw_html)
    # raw_html = re.sub(re_lsd, ' ', raw_html)

    raw_html = re.sub(r'(<)?[^<]+margin-bottom[^>]+(>)?', '', raw_html)
    raw_html = re.sub(r'(<)?[^<]+:justify[^>]+(>)?', '', raw_html)
    raw_html = re.sub(r'(<)?[^<]+font-[^>]+(>)?', '', raw_html)

    raw_html = re.sub(r'<span[^>]+(>)?', '', raw_html)
    raw_html = re.sub(r'</span>', '', raw_html)

    raw_html = raw_html.replace('&iacute;', 'í')
    raw_html = raw_html.replace('&aacute;', 'á')

    re_tags = re.compile(r'<.*?>')
    re_comments = re.compile(r'<!--.*?-->', flags=re.MULTILINE)
    re_empty_line = re.compile(r'\n\s*\n', flags=re.MULTILINE)
    raw_html = re.sub(re_tags, '', raw_html)
    raw_html = re.sub(re_nbsp, ' ', raw_html)
    raw_html = re.sub(re_comments, '', raw_html)
    raw_html = re.sub(re_empty_line, '\n\n', raw_html)

    raw_html = raw_html.replace('<!--', '')

    return raw_html


def find_files(which: str, where: str='.') -> List[str]:
    rule = re.compile(fnmatch.translate(which), re.IGNORECASE)
    return [name for name in os.listdir(where) if rule.match(name)]


def extract_date(year: int, text: str) -> Optional[date]:
    m = re.search(r'\D(\d{1,2})\.(\d{1,2})\.', text)
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
