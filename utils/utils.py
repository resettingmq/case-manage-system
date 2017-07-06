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
    def __init__(self, title=None, field=None):
        self.title = title
        self._field = field

    @classmethod
    def get_instance_from_field(cls, field):
        dt_column = cls(field=field)
        dt_column.title = field.verbose_name
        return dt_column


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

        d['_declared_columns'] = OrderedDict(declared_columns)

        meta_defined_columns = []
        field_names = getattr(meta, 'fields', [])
        for field_name in field_names:
            filed = _get_field(model, field_name)
            if field is None:
                continue
            dt_column = DataTablesColumn.get_instance_from_field(field)
            meta_defined_columns.append((field_name, dt_column))
        d['_meta_defined_columns'] = OrderedDict(meta_defined_columns)

        column_order = getattr(meta, 'column_order', None)
        if column_order is None:
            columns = OrderedDict(declared_columns)
            for name, column in d['_meta_defined_columns'].items():
                if name not in columns:
                    columns[name] = column
        else:
            columns = OrderedDict()
            for name in column_order:
                if name in d['_declared_columns']:
                    columns[name] = d['_declared_columns'][name]
                elif name in d['_meta_defined_columns']:
                    columns[name] = d['_meta_defined_columns'][name]
        d['columns'] = columns

        return super().__new__(mcls, name, bases, d)

    @classmethod
    def __prepare__(mcls, name, bases):
        return OrderedDict()


class ModelDataTable(metaclass=ModelDataTableMetaClass):
    @classmethod
    def get_field_names(cls):
        return cls.columns.keys()
