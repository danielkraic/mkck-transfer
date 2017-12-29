from mkck.year import get_year_events_list
from wordpress.importer import Importer

wp_url = 'http://localhost:8000'
wp_username = ''
wp_password = ''

w = Importer(url=wp_url, username=wp_username, password=wp_password)


def import_year(year: int) -> None:
    events = get_year_events_list(year=year)
    for event in events:
        w.import_post(event=event)


def remove_year(year: int) -> None:
    w.remove_year_items(year=year)


def main() -> None:
    year = 2010

    import_year(year=year)
    w.create_year_page(year=year)

    # remove_year(year=year)


if __name__ == '__main__':
    main()
