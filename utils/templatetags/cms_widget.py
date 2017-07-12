# -*- coding: utf-8 -*-

"""
Widgets for rendering cms related front-end components
"""

import os
from django import template
from django.forms.fields import CheckboxInput

register = template.Library()


class InfoBoxNode(template.Node):
    template_dir = 'components/infobox'
    file_prefix = 'infobox_'
    file_suffix = '.html'

    def __init__(self, entity_name):
        self.entity_name = entity_name

    def render(self, context):
        try:
            entity_name = self.entity_name.resolve(context)
        except AttributeError:
            entity_name = self.entity_name
        template_name = '{}{}{}'.format(self.file_prefix, entity_name, self.file_suffix)
        template_name = os.path.join(self.template_dir, template_name)
        t = context.template.engine.get_template(template_name)

        new_context = template.Context()
        new_context['infobox'] = context['infobox_dict'][entity_name]
        return t.render(new_context)


@register.tag
def render_infobox(parser, token):
    """
    :usage: {% render_infobox "client" %}
    """
    try:
        tag_name, entity_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            '{} tag requires exactly one argument: entity name'.format(token.contents.split()[0])
        )
    print(entity_name)
    if entity_name[0] == entity_name[-1] and entity_name[0] in ('"', "'"):
        entity_name = entity_name[1:-1]
    else:
        entity_name = template.Variable(entity_name)

    return InfoBoxNode(entity_name)


@register.filter
def is_checkbox(field):
    return isinstance(field.field.widget, CheckboxInput)
