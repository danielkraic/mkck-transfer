from datetime import datetime
from typing import List, Dict, Optional

from wordpress_xmlrpc import Client, WordPressPost, WordPressPage
from wordpress_xmlrpc.methods.posts import NewPost

from mkck.debug import notice
from mkck.event import Event
from mkck.utils import format_iso_date
from mkck.year_page import get_year_page_content, EventLink
from wordpress.api import WordpressAPI
from wordpress.errors import ImporterError


class Importer(object):
    def __init__(self, url: str, username: str, password: str) -> None:
        self._client: Client = Client(url='{}/xmlrpc.php'.format(url), username=username, password=password)
        self._api: WordpressAPI = WordpressAPI(url=url, username=username, password=password)

    def create_event_post(self, event: Event) -> None:
        images = self.get_event_photos(year=event.year, event_number=event.event_number, is_planned=event.is_planned)

        post = WordPressPost()
        post.post_status = 'publish'
        post.title = event.title
        post.content = event.get_content(images=images)

        post_date = event.date
        if post_date:
            post.date = datetime(year=post_date.year, month=post_date.month, day=post_date.day)

        post.terms_names = _get_tags(year=event.year, is_planned=event.is_planned)

        post_id = self._client.call(NewPost(post))
        notice('Imported post {}. {}'.format(post_id, event))

    def upload_event_photos(self, event: Event) -> List[int]:
        return self._api.upload_images(images=event.photos, publish_date=event.date)

    def get_event_photos(self, year: int, event_number: int, is_planned: bool=True) -> List[int]:
        return self._api.get_post_images(year=year, event_number=event_number, is_planned=is_planned)

    def remove_year_items(self, year: int) -> None:
        date_from, date_to = self._api.get_year_date_range(year=year)

        for item_type in ['posts', 'pages']:
            items = self._api.get_items(item_type=item_type, date_from=date_from, date_to=date_to)
            notice('{} items to remove: {}'.format(item_type, len(items)))
            for item_id in [item['id'] for item in items]:
                self._api.remove_items(item_type=item_type, item_id=item_id)

    def create_year_page(self, year: int) -> None:
        date_from, date_to = self._api.get_year_date_range(year=year)

        posts = self._api.get_items(item_type='posts', date_from=date_from, date_to=date_to)
        posts = sorted(posts, key=lambda item: item['date'])

        categories = self._api.get_items(item_type='categories', search='{}_'.format(year))

        category_planned = _get_planned_category(categories=categories)
        category_not_planned = _get_not_planned_category(categories=categories)

        posts_planned = [post for post in posts if category_planned in post['categories']]
        posts_not_planned = [] if not category_not_planned \
            else [post for post in posts if category_not_planned in post['categories']]

        events_planned = [EventLink(event_number=i+1,
                                    title=post['title']['rendered'],
                                    link=post['link'],
                                    date=format_iso_date(post['date']))
                          for i, post in enumerate(posts_planned)]

        events_not_planned = [EventLink(event_number=i + 1,
                                        title=post['title']['rendered'],
                                        link=post['link'],
                                        date=format_iso_date(post['date']))
                              for i, post in enumerate(posts_not_planned)]

        page = WordPressPage()
        page.post_status = 'publish'
        page.title = 'Akcie {}'.format(year)
        page.content = get_year_page_content(events_planned=events_planned, events_non_planned=events_not_planned)
        page.date = datetime(year=year, month=1, day=1)

        page_id = self._client.call(NewPost(page))
        notice('Created page {} for year {}'.format(page_id, year))


def _get_tags(year: int, is_planned: bool) -> Dict[str, List[str]]:
    res = {
        'post_tag': ['imported', 'rok_{}'.format(year)],
        'category': ['Akcie', 'Akcie_{}'.format(year)]
    }

    if is_planned:
        res['post_tag'].append('rok_{}_planovane'.format(year))
        res['category'].append('Akcie_{}_planovane'.format(year))
    else:
        res['post_tag'].append('rok_{}_mimo_plan'.format(year))
        res['category'].append('Akcie_{}_mimo_plan'.format(year))

    return res


def _get_planned_category(categories: List[dict]) -> int:
    for category in categories:
        if category['name'].endswith('planovane'):
            return category['id']

    raise ImporterError('Failed to get category "planned".')


def _get_not_planned_category(categories: List[dict]) -> Optional[int]:
    for category in categories:
        if category['name'].endswith('mimo_plan'):
            return category['id']

    return None

