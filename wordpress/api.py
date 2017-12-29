from datetime import date, datetime
from typing import List, Optional, Tuple

import requests
from requests.auth import HTTPBasicAuth

from mkck.debug import notice
from mkck.gallery import GalleryItem, temporary_image


class WordpressAPI(object):
    def __init__(self, url: str, username: str, password: str):
        self._api_url = '{}/wp-json/wp/v2'.format(url)
        self._username = username
        self._password = password

    def upload_images(self, images: List[GalleryItem], publish_date: Optional[date]) -> List[int]:
        resp = []

        for image in images:
            try:
                with temporary_image(path=image.path, name=image.name) as tmp_image:
                    image_id = self.upload_image(image=tmp_image, caption=image.caption, publish_date=publish_date)
                    resp.append(image_id)
            except requests.HTTPError as error:
                print('Failed to upload image. Error: {}'.format(error))
                raise error

        return resp

    def upload_image(self, image: str, caption: str, publish_date: Optional[date]) -> int:
        data = {
            'file': open(image, 'rb'),
        }

        payload = {
            'caption': caption,
            'title': caption,
        }

        if publish_date:
            payload['date'] = datetime(year=publish_date.year,
                                       month=publish_date.month,
                                       day=publish_date.day).isoformat()

        resp = requests.post(url=self._api_url + '/media', auth=HTTPBasicAuth(self._username, self._password),
                             files=data, data=payload)
        resp.raise_for_status()

        image_id = resp.json()['id']

        notice('Imported image {}. {}: {}'.format(image_id, image, caption))
        return image_id

    @staticmethod
    def get_year_date_range(year: int) -> Tuple[datetime, datetime]:
        date_from = datetime(year=year - 1, month=12, day=31, hour=23, minute=59, second=59)
        date_to = datetime(year=year + 1, month=1, day=1, hour=0, minute=0, second=0)

        return date_from, date_to

    def get_items(self, item_type: str, date_from: datetime, date_to: datetime) -> List[dict]:
        payload = {
            'after': date_from.isoformat(),
            'before': date_to.isoformat(),
            'per_page': 100,
        }

        resp = requests.get(url=self._api_url + '/' + item_type, auth=HTTPBasicAuth(self._username, self._password),
                            params=payload)
        resp.raise_for_status()
        return resp.json()

    def remove_items(self, item_type, item_id):
        resp = requests.delete(url=self._api_url + '/{}/{}'.format(item_type, item_id),
                               auth=HTTPBasicAuth(self._username, self._password))
        resp.raise_for_status()
        notice('removed {} with id {}'.format(item_type, item_id))
