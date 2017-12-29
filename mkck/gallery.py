from contextlib import contextmanager
import os
import shutil

from mkck.config import DIR_PHOTOS_UPLOAD_TMP
from mkck.debug import debug


class GalleryItem(object):
    def __init__(self, year: int, event_number: int, image_number: int, path: str, caption: str, is_planned: bool=True):
        self.path = path
        self.caption = caption
        self.name = '{year}-{planned}{event_number:02d}-{image_number:02d}.jpg'.format(
            year=year,
            planned='' if is_planned else 'mp-',
            event_number=event_number,
            image_number=image_number)


@contextmanager
def temporary_image(path, name) -> str:
    dst = '{}/{}'.format(DIR_PHOTOS_UPLOAD_TMP, name)

    shutil.copy(src=path, dst=dst)
    debug('tmp img "{}" created'.format(dst))

    yield dst

    os.remove(path=dst)
    debug('tmp img "{}" removed'.format(dst))
