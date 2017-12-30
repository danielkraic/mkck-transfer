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
                {events_planned_str}
              </td>
              <td width="49%">
                <h4><strong>Akcie mimo plánu</strong></h4>
                {events_non_planned_str}
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
    events_planned_str = _get_events_paragraph(events=events_planned)
    events_non_planned_str = _get_events_paragraph(events=events_non_planned)
    return year_page_template.format(
        events_planned_str=events_planned_str,
        events_non_planned_str=events_non_planned_str)


def _get_events_paragraph(events: List[EventLink]) -> str:
    if not events:
        return ''

    res = ''
    for event in events:
        res += '{event_number}. <a href="{link}">{title}{date}</a><br />'.format(
            event_number=event.event_number, link=event.link, title=event.title, date=event.date)
    return '<p>{}</p>'.format(res)
