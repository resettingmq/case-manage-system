# -*- coding: utf-8 -*-

from collections import OrderedDict
from django.core.exceptions import ImproperlyConfigured, FieldDoesNotExist
from django.db.models.base import ModelBase


def _get_field(model, field_name):
    if not isinstance(field_name, str):
        raise ValueError('field_name {} should be a str'.format(field_name))
    if field_name.startswith('__'):
        return None
    if '__' in field_name:
        related_model_name, related_field_name = field_name.split('__', 1)
        related_model = model._meta.get_field(related_model_name).related_model
        return _get_field(related_model, related_field_name)
    try:
        field = model._meta.get_field(field_name)
    except FieldDoesNotExist:
        field = None
    finally:
        return field


class DataTablesColumn:
    pass


class ModelDataTableMetaClass(type):
    def __new__(mcls, name, bases, attrs):
        if not bases:
            d = dict(attrs)
            return super().__new__(mcls, name, bases, d)

        meta = attrs.get('Meta')
        if not meta or getattr(meta, 'model', None) is None:
            raise ImproperlyConfigured('model attribute of Meta class is missing'
                                       'in {} class definition'.format(name))

        model = meta.model
        if not isinstance(model, ModelBase):
            raise ImproperlyConfigured('The model specified in Meta is not a models.Model instance.')

        d = dict(attrs)
        declared_columns = []
        for name, value in attrs.items():
            if isinstance(value, DataTablesColumn):
                field = _get_field(model, name)
                if field is None:
                    continue
                value._field = field
                declared_columns.append((name, value))
                d.pop(name)
        del attrs

        d['declared_columns'] = declared_columns
        print("I'm here")
        return super().__new__(mcls, name, bases, d)

    @classmethod
    def __prepare__(mcls, name, bases):
        return OrderedDict()


class ModelDataTable(metaclass=ModelDataTableMetaClass):
    @classmethod
    def get_field_names(cls):
        return [column[0] for column in cls.declared_columns]
