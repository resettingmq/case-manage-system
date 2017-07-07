from django.shortcuts import render
from django.views import generic
from django.http import JsonResponse
from django.core.exceptions import ImproperlyConfigured

# Create your views here.


class JsonContextMixin:
    def get_json_context_data(self, **kwargs):
        """
        : 生成JsonResponse的数据
        :param kwargs: 需要添加进返回值的键值对
        :return: dict, JsonResponse的数据
        """
        return kwargs


class JsonResponseMixin:
    json_response_class = JsonResponse

    def render_to_json_response(self, context, **response_kwargs):
        """
        : 生成JsonResonse对象并返回
        :param context: JsonResponse对象所包含的data
        :param response_kwargs: JsonResponse对象初始化所需要的其他参数，可为空
        :return: 所生成的JsonResponse对象
        """
        return self.json_response_class(context, **response_kwargs)


class DataTablesMixin(JsonResponseMixin, JsonContextMixin):
    """
    : 这个Mixin不应该被单独使用，它依赖与定义了get_context_data()的类
    """
    dt_data_src = 'data'
    dt_config = None
    dt_column_fields = None
    dt_table_name = None

    def get_dt_data_src(self):
        return self.dt_data_src

    def get_dt_config(self):
        if self.dt_config is None:
            raise ImproperlyConfigured('ModelDataTables is not properly setted in DataTablesMixin')
        return self.dt_config

    def get_dt_table_name(self):
        if self.dt_table_name is not None:
            return self.dt_table_name
        dt_config = self.get_dt_config()
        return self.dt_config.table_id

    def get_dt_column_fields(self):
        """
        : 生成DataTables实例所期望的model field names集合
        :return: list, model field names 列表
        """
        # if self.dt_column_fields is not None:
        #     return self.dt_column_fields
        # try:
        #     model = self.get_queryset().model
        #     dt_column_fields = model.DataTablesMeta.column_fields.keys()
        # except AttributeError:
        #     return []
        # else:
        #     return dt_column_fields
        return self.dt_config.get_field_names()

    def get_json_context_data(self):
        """
        : 依赖于其他class的get_queryset()方法
        :return: dict
        """
        dt_column_fields = self.get_dt_column_fields()
        json_context = {
            self.dt_data_src: list(self.get_queryset().values(*dt_column_fields))
        }
        return super().get_json_context_data(**json_context)

    def get_context_data(self, dt_config=None, **kwargs):
        """
        : 将ModelDataTables类添加进context
        : 需要依赖与其他class或者mixin
        :param dt_config: 指定外部的ModelDataTables类
        :param kwargs: 额外的命名参数
        :return: context
        """
        datatables_config = dt_config if dt_config is not None else self.get_dt_config()
        datatables_id = datatables_config.table_id
        kwargs.update(
            dt_config=datatables_config,
            dt_id=datatables_id
        )
        return super().get_context_data(**kwargs)


class DataTablesListView(DataTablesMixin, generic.ListView):

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            # if not self.dt_config.dt_serverSide:
                return self.render_to_json_response(self.get_json_context_data())
        return super().get(request, *args, **kwargs)
