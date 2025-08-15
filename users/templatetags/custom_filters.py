from django import template

register = template.Library()

@register.filter
def split(value, delimiter=','):
    """
    Split a string by delimiter and return a list.
    Usage: {{ value|split:',' }}
    """
    if not value:
        return []
    return [item.strip() for item in value.split(delimiter)]

@register.filter
def trim(value):
    """
    Trim whitespace from a string.
    Usage: {{ value|trim }}
    """
    if not value:
        return ''
    return value.strip()