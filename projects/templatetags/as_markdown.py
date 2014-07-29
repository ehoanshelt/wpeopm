import markdown

from django import template

register = template.Library()

@register.filter
def as_markdown(text):
	return markdown.markdown(text)
