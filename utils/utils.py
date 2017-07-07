# -*- coding: utf-8 -*-

from collections import OrderedDict
from django.core.exceptions import ImproperlyConfigured, FieldDoesNotExist
from django.db.models.base import ModelBase
from django.db.models.fields import Field


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
        if field is not None:
            self._initialize_from_field(field)
        else:
            self._bound = False

    @property
    def field(self):
        raise AttributeError('Attribute field not defined, try _field')

    @field.setter
    def field(self, value):
        self._initialize_from_field(value)

    def _initialize_from_field(self, field):
        if not isinstance(field, Field):
            raise ValueError('Not an instance of django Field')
        if self.title is None:
            self.title = field.verbose_name
        self._field = field
        self._bound = True

    def get_dt_config(self):
        dt_config = {}
        dt_config['data'] = self.name
        return dt_config

    @classmethod
    def get_instance_from_field(cls, field):
        dt_column = cls(field=field)
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

        # 处理声明式定义的columns
        d = dict(attrs)
        declared_columns = []
        for name, value in attrs.items():
            if isinstance(value, DataTablesColumn):
                field = _get_field(model, name)
                if field is None:
                    continue
                value.name = name
                value.field = field
                declared_columns.append((name, value))
                d.pop(name)
        d['_declared_columns'] = OrderedDict(declared_columns)

        # 处理从Meta class属性中读取fields-columns的信息
        # todo: 实现从Fields中读取更多的配置信息，这里之实现了读取field_name
        meta_defined_columns = []
        field_names = getattr(meta, 'fields', [])
        for field_name in field_names:
            field = _get_field(model, field_name)
            if field is None:
                continue
            dt_column = DataTablesColumn.get_instance_from_field(field)
            dt_column.name = field_name
            meta_defined_columns.append((field_name, dt_column))
        d['_meta_defined_columns'] = OrderedDict(meta_defined_columns)

        # 处理两种columns源的order，并生成最终的columns属性
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

        # 处理js配置属性，dt_开头的类属性
        js_config = {}
        for name, value in attrs.items():
            if name.startswith('dt_'):
                attr_name = name.split('dt_', 1)[1]
                js_config[attr_name] = value
        d['js_config'] = js_config

        d['table_id'] = 'dt-{}'.format(model._meta.model_name)

        return super().__new__(mcls, name, bases, d)

    @classmethod
    def __prepare__(mcls, name, bases):
        return OrderedDict()


class ModelDataTable(metaclass=ModelDataTableMetaClass):
    @classmethod
    def get_field_names(cls):
        """
        : 指定json数据中包含的fields，用于对请求的处理函数中
        :return: list，json数据中应该包含的fields
        """
        return cls.columns.keys()

    @classmethod
    def get_titles(cls):
        """
        : 返回用于HTML table header显示的列名
        :return: list
        """
        return [column.title for column in cls.columns.values()]

    @classmethod
    def get_dt_config_columns(cls):
        """
        用于生成DataTables cloumns相关的配置属性
        :return: list，每个元素代表一个column的配置
        """
        return [c.get_dt_config() for c in cls.columns.values()]

    @classmethod
    def get_dt_config(cls):
        """
        用于生成DataTables相关的配置属性
        :return: dict，每个key指向一个配置项
        """
        config = dict(cls.js_config)
        config['columns'] = cls.get_dt_config_columns()
        return config
