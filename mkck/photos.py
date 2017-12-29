from collections import namedtuple
from os.path import join
from typing import List, Optional

from bs4 import BeautifulSoup, Tag

from mkck.utils import find_files


PhotoItem = namedtuple('Photo', ['path', 'desc'])


def get_photos(photos_file: str, photos_dir: str) -> List[PhotoItem]:
    photos_with_desc = _get_event_photos(file=photos_file)

    photo_files_all = find_files(which='*.jpg', where=photos_dir)
    photo_files_fn = find_files(which='*_tn.jpg', where=photos_dir)
    photo_files = {p.split('/')[-1]: p for p in photo_files_all if p not in photo_files_fn}

    photos_with_desc = [PhotoItem(path=join(photos_dir, photo_files.get(photo.path)), desc=photo.desc)
                        for photo in photos_with_desc]
    return photos_with_desc


def _get_event_photos(file: str) -> List[PhotoItem]:
    res = []

    with open(file, 'r') as f:
        last_img = None
        soup = BeautifulSoup(f.read(), 'html.parser')

        for sibling in soup.p.next_siblings:
            if not isinstance(sibling, Tag):
                continue

            img = _get_img(sibling)
            if img:
                if last_img:
                    res.append(PhotoItem(path=last_img, desc=''))

                last_img = img.split('/')[-1]
            else:
                description = str(sibling.text).replace(u'\xa0', u' ').strip()
                if description and description != '' and not description.startswith('Stránka MKCK '):
                    if last_img:
                        description = description.splitlines()[0]
                        res.append(PhotoItem(path=last_img, desc=description))
                        # debug('img: {} {}'.format(last_img, description))
                        last_img = None

    if last_img:
        res.append(PhotoItem(path=last_img, desc=''))
        # debug('img: {}'.format(last_img))

    return res


def _get_img(element) -> Optional[str]:
    imgs = element.find_all('img')
    for img in imgs:
        src = img['src']
        if not src:
            return None

        return src

    return None
