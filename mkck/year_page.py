from typing import List
from collections import namedtuple

from jinja2 import Template


EventLink = namedtuple('Event', ['event_number', 'title', 'link', 'date'])


year_page_template = '''
<table width="100%">
  <tbody>
    <tr>
      <td>
        <table width="100%">
          <tbody>
            <tr>
              <td width="50%">
                <h4><strong>Plánované akcie</strong></h4>
                <p>
                  {% for item in events_planned %}
                    {{item.event_number}}. <a href="{{item.link}}">{{item.title}}{{item.date}}</a><br />
                  {% endfor %}
                </p>
              </td>
              <td width="49%">
                <h4><strong>Akcie mimo plánu</strong></h4>
                <p>
                  {% for item in events_non_planned %}
                    {{item.event_number}}. <a href="{{item.link}}">{{item.title}}{{item.date}}</a><br />
                  {% endfor %}
                </p>
              </td>
            </tr>
          </tbody>
        </table>
      </td>
    </tr>
  </tbody>
</table>
'''


def get_year_page_content(events_planned: List[EventLink], events_non_planned: List[EventLink]) -> str:
    return Template(year_page_template).render(events_planned=events_planned, events_non_planned=events_non_planned)
