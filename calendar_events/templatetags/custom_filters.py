from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def get_abs(value):
    if value < 0:
        return f"{abs(value)} p.n.e."
    else:
        return f"{value}"