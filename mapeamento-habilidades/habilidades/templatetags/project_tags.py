from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def split_string(value, separator=','):
    """
    Divide uma string em uma lista usando um separador (padrão é vírgula).
    Também limpa espaços em branco em cada item.
    Uso: {{ string_de_habilidades|split_string:", " }}
    """
    if not value:
        return []
    
    # Divide a string e remove espaços em branco antes/depois de cada item
    return [item.strip() for item in value.split(separator)]