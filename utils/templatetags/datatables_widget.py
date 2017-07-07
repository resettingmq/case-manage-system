# -*- coding: utf-8 -*-

from django.template import Library
from django.utils.safestring import mark_safe
from django.core.serializers.json import DjangoJSONEncoder
import json

register = Library()


@register.inclusion_tag('dt_templates/dt_tabel.html')
def render_table(dt_config, class_=None):
    titles = dt_config.get_titles()
    return {'dt_config': dt_config, 'titles': titles, 'class': class_}


@register.inclusion_tag('dt_templates/dt_jsscript.html')
def render_js_script(dt_config):
    table_id = dt_config.table_id
    dt_config = dt_config.get_dt_config()
    return {'table_id': table_id, 'dt_config': dt_config}


@register.filter(name='json')
def json_filter(value):
    return mark_safe(json.dumps(value, cls=DjangoJSONEncoder))
