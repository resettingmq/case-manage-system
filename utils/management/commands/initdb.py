# -*- coding: utf-8 -*-

import logging
from django.core.management import BaseCommand
from django.core.management.base import CommandError
from django.apps import apps


def _get_dependent_models(model):
    return [f.related_model for f in model._meta.get_fields()
            if f.related_model != model and (f.one_to_one or f.many_to_one) and f.concrete]


def _populate_model(model):
    try:
        model.populate()
    except AttributeError:
        logging.warning('model {} does not support populate()'
                        .format(model._meta.verbose_name))


def _check_all_dependent_model_initialized(dependencies, initialized):
    for d in dependencies:
        if d not in initialized:
            return False
    return True


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('app_label', action='store', nargs='?')
        parser.add_argument('model_name', action='store', nargs='?')

    def handle(self, *args, **options):
        all_models = apps.get_models()

        if options['app_label'] is None:
            target_models = all_models
            initialized = []
        else:
            try:
                target_app = apps.get_app_config(options['app_label'])
            except LookupError as e:
                raise CommandError('app {} not found'.format(options['app_label']))
            if options['model_name'] is None:
                target_models = target_app.get_models()
            else:
                try:
                    target_models = [target_app.get_model(options['model_name']), ]
                except LookupError:
                    raise CommandError('model {} not found'.format(options['model_name']))
            # 需要将iterator转为list
            # 因为not in操作有可能提前将iterator耗尽
            target_models = list(target_models)
            initialized = [m for m in all_models if m not in target_models]
        init_target = [[m, False, _get_dependent_models(m)] for m in target_models]

        init_target_len = len(init_target)
        count = 0
        while init_target_len > count:
            for m in init_target:
                if m[1]:
                    continue
                if _check_all_dependent_model_initialized(m[2], initialized):
                    initialized.append(m[0])
                    _populate_model(m[0])
                    m[1] = True
                    count += 1
