from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    """Multiplica el valor por un argumento"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0
