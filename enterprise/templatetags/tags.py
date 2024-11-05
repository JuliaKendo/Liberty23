from django import template
from django.template import Template, Context
from django.template.loader import render_to_string
from contextlib import suppress
from more_itertools import first


register = template.Library()


@register.filter
def html_content(content):
    template = Template(content)
    rendered_html = template.render(Context({}))
    return rendered_html

