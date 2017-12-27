from typing import Dict, Optional

from bs4 import BeautifulSoup, Tag


def get_event_photos(file: str) -> Dict[str, str]:
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