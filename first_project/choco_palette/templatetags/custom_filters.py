
from django import template
register = template.Library()

@register.filter(name='getlist')
def getlist(querydict, key):
    return querydict.getlist(key)