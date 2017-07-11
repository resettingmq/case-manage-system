# -*- coding: utf-8 -*-

"""
Widgets for rendering cms related front-end components
"""

import os
from django import template

register = template.Library()


class InfoBoxNode(template.Node):
    template_dir = 'components/infobox'
    file_prefix = 'infobox_'
    file_suffix = '.html'

    def __init__(self, entity_name):
        template_name = '{}{}{}'.format(self.file_prefix, entity_name, self.file_suffix)
        self.template_name = os.path.join(self.template_dir, template_name)

    def render(self, context):
        t = context.template.engine.get_template(self.template_name)
        return t.render(context)


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
    if entity_name[0] in ('"', "'"):
        entity_name = entity_name[1:]
    if entity_name[-1] in ('"', "'"):
        entity_name = entity_name[:-1]

    return InfoBoxNode(entity_name)
