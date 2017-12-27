from typing import Optional, List

from wordpress_xmlrpc import Client, WordPressPost, WordPressPage
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost
from wordpress_xmlrpc.methods.users import GetUserInfo

from akcia import get_year_list

# def wp():
#     wp = Client(url='https://nova.mkck.sk/xmlrpc.php', username='kraic', password='5*176UHb#*6x1EPEk2ye')
#     res = wp.call(method=GetPosts())
#
#     print('res:{}'.format(len(res)))
#     for item in res:
#         print(item)


def print_year(year) -> None:
    print(year)

    for akcia in get_year_list(year=year):
        print(akcia)


def main() -> None:
    for year in range(2010, 2017):
        print_year(year=year)


if __name__ == '__main__':
    main()
