from django import template

register = template.Library()

@register.filter
def split_comma(value):
    """
    Divide uma string por vírgulas e retorna uma lista de itens limpos.
    """
    if isinstance(value, str):
        return [item.strip() for item in value.split(',') if item.strip()]
    return []