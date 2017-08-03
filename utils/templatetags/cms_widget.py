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

    def __init__(self, entity_name, infobox_type):
        self.entity_name = entity_name
        self.type = infobox_type

    def render(self, context):
        try:
            entity_name = self.entity_name.resolve(context)
        except AttributeError:
            entity_name = self.entity_name
        file_suffix = self.file_suffix
        if self.type == 'small':
            file_suffix = '_small' + file_suffix
        template_name = '{}{}{}'.format(self.file_prefix, entity_name.split('.')[1], file_suffix)
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
        tag_name, entity_name, infobox_type = token.split_contents()
    except ValueError:
        try:
            tag_name, entity_name = token.split_contents()
            infobox_type = 'normal'
        except ValueError:
            raise template.TemplateSyntaxError(
                '{} tag requires exactly one or two argument(s): entity name'.format(token.contents.split()[0])
            )
    if entity_name[0] == entity_name[-1] and entity_name[0] in ('"', "'"):
        entity_name = entity_name[1:-1]
    else:
        entity_name = template.Variable(entity_name)
    if infobox_type[0] == infobox_type[-1] and infobox_type[0] in ('"', "'"):
        infobox_type = infobox_type[1:-1]

    return InfoBoxNode(entity_name, infobox_type)


@register.filter
def is_checkbox(field):
    return isinstance(field.field.widget, CheckboxInput)


@register.inclusion_tag('components/form.html', takes_context=True)
def render_form(context):
    # return {
    #     'form': form,
    #     'title': title,
    #     'show_button': show_button,
    #     'button_value': button_value,
    # }
    return context
