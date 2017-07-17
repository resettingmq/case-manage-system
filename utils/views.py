from functools import reduce
from collections import OrderedDict
from django.views import generic
from django.http import JsonResponse, HttpResponseRedirect
from django.core.exceptions import ImproperlyConfigured, SuspiciousOperation
from django.apps import apps
from django.utils.module_loading import import_string

from utils.utils import ModelDataTable

from cms import site_config


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
    dt_table_id = None

    def get_dt_data_src(self):
        return self.dt_data_src

    def get_dt_config(self):
        if self.dt_config is None:
            raise ImproperlyConfigured('ModelDataTables is not properly setted in DataTablesMixin')
        return self.dt_config

    def get_dt_table_name(self):
        if self.dt_table_id is not None:
            return self.dt_table_id
        dt_config = self.get_dt_config()
        return self.dt_config.table_id

    def is_server_side(self):
        return bool(self.dt_config.dt_serverSide)

    def get_dt_query_fields(self):
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
        return self.dt_config.get_query_fields()

    def get_json_context_data(self, http_queryset=None):
        """
        : 依赖于其他class的get_queryset()方法
        : 包含了数据获取，处理的逻辑
        :return: dict
        """
        json_context = {}

        dt_column_fields = self.get_dt_query_fields()
        queryset = self.get_queryset()
        if self.is_server_side():
            if http_queryset is None:
                raise ValueError('No GET queryset passed in for server-side mode')

            try:
                draw = int(http_queryset.get('draw'))
            except ValueError:
                json_context.update(error='Invalid request arguments')
                return super().get_json_context_data(**json_context)
            else:
                json_context.update(draw=draw)
            records_total = queryset.count()
            json_context.update(recordsTotal=records_total)

            # 处理filter
            # 只实现了对全局的搜索
            # 没有实现对指定列的搜索
            pattern = http_queryset.get('search[value]')
            is_regex = http_queryset.get('search[regex]') == 'true'
            queryset = queryset.filter(
                reduce(
                    lambda x, y: x | y,
                    [c.get_filter_q_object(pattern, is_regex) for c in self.dt_config.columns.values()]
                )
            )
            records_filtered = queryset.count()
            json_context.update(recordsFiltered=records_filtered)

            # 处理order
            order_dir = '' if http_queryset['order[0][dir]'] == 'asc' else '-'
            order_column = list(self.dt_config.columns.values())[int(http_queryset['order[0][column]'])].name
            queryset = queryset.order_by(order_dir + order_column)

            # 处理分页
            page_start = int(http_queryset['start'])
            page_length = int(http_queryset['length'])
            queryset = queryset[page_start:page_start + page_length]

        json_context[self.dt_data_src] = list(queryset.values(*dt_column_fields))

        return super().get_json_context_data(**json_context)

    def get_context_data(self, **kwargs):
        """
        : 将ModelDataTables类添加进context
        : 需要依赖与其他class或者mixin
        :param dt_config: 指定外部的ModelDataTables类
        :param kwargs: 额外的命名参数
        :return: context
        """
        if 'dt_config' not in kwargs:
            kwargs['dt_config'] = self.get_dt_config()

        return super().get_context_data(**kwargs)


class DataTablesListView(DataTablesMixin, generic.ListView):

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            # if not self.dt_config.dt_serverSide:
                return self.render_to_json_response(self.get_json_context_data(request.GET))
        return super().get(request, *args, **kwargs)


class InfoboxMixin:
    view_name = None
    infobox_list = None

    def get_infobox_dict(self):
        infobox_list = self.infobox_list
        if infobox_list is None:
            view_name = self.view_name
            if view_name is None:
                raise ImproperlyConfigured('Require a name for this view.')
            view_config = site_config.VIEWS.get(view_name)
            if view_config is None:
                return {}
            infobox_list = view_config.get('INFO_BOXES')
            if infobox_list is None:
                return {}
        ret = []
        for infobox_name in infobox_list:
            try:
                # infobox_conf = site_config.INFO_BOXES[infobox_name]
                model = apps.get_model(infobox_name)
            except (AttributeError, KeyError):
                raise ImproperlyConfigured('Require info box model configuration for {}'.format(infobox_name))
            except ValueError:
                raise ImproperlyConfigured('info box model format error: {}'.format(infobox_name))
            except LookupError:
                raise ImproperlyConfigured('info box model not found: {}'.format(infobox_name))

            count = model._default_manager.count()
            ret.append((infobox_name, {'related_entity_name': infobox_name, 'count': count}))

        return OrderedDict(ret)

    def get_context_data(self, **kwargs):
        kwargs.update(infobox_dict=self.get_infobox_dict())
        return super().get_context_data(**kwargs)


class RelatedEntityConstructMixin(InfoboxMixin, DataTablesMixin, generic.list.MultipleObjectMixin):
    main_entity = None
    action = None
    # config dict 存储与main_entity相关model的信息
    related_entity_config = None

    def is_related(self):
        return self.model is not self.main_entity

    def process_query_args(self):
        """
        : 用于获取url query string中与related entity相关信息
        : 包括realted以及action
        :return: boolean，指示query_args中是否有有效数据
        """
        if self.request.method == 'POST':
            return False
        if 'clear' in self.request.GET:
            try:
                del self.request.session['current_entity_name']
                del self.request.session['action']
            except KeyError:
                pass
            return True
        current_entity_name = self.request.GET.get('current', '')
        action = self.request.GET.get('action', None)
        if current_entity_name and current_entity_name != self.request.session.get('current_entity_name'):
            try:
                apps.get_model(current_entity_name)
                self.request.session['current_entity_name'] = current_entity_name
                self.request.session['action'] = self.request.GET.get('action', 'list')
            except (LookupError, ValueError):
                return False
            return True
        if action and action != self.request.session['action']:
            self.request.session['action'] = action
            return True
        return False

    def process_session(self):
        """
        : 获取session中的related_entity_name, 以及action
        : 并根据related_entity_str设置self.model
        :return: 
        """
        current_entity_name = self.request.session.get('current_entity_name', '')
        try:
            self.main_entity = self.model
            self.model = apps.get_model(current_entity_name)
            self.action = self.request.session.get('action', None)
        except (LookupError, ValueError):
            pass
        else:
            return

    def construct_related_entity(self):
        """
        : 进行流程控制，以及相关Mixin的初始化工作
        :return: 
        """
        if self.process_query_args():
            return True
        self.process_session()
        # 设置infobox相关属性
        self.infobox_list = self.get_related_entity_config().keys()
        # 设置object_list，因为继承了MultipleObjectMixin，
        # 在它的get_context_data()中，读取了这个值
        # 这个情况比较诡异，虽然MultipleObjectMixin中可以根据关键字参数设置object_list
        # 但是它用到了pop('object_list', self.object_list)
        # 即便是字典中有'object_list'这个键，还是会evaluate self.object_list!!!
        self.object_list = self.get_queryset()

        if not self.is_related() or self.action == 'create':
            # 获取form的fields信息
            # 设置DatatablesMixin的依赖，避免报错
            try:
                modelform_name = self.model.get_modelform_name()
                self.form_class = import_string(modelform_name)
            except (AttributeError, ImportError):
                pass
            try:
                self.fields = self.model.get_form_fields()
            except AttributeError:
                pass
            if self.fields == None and self.form_class == None:
                raise ImproperlyConfigured('form_class or fields are not properly configured for model {}:{}'
                                           .format(self.model._meta.app_label, self.model._meta.verbose_name))
        else:
            try:
                datatables_class = self.model.datatables_class
            except:
                raise ImproperlyConfigured('No datatables class configured in {}:{}'
                                           .format(self.model._meta.app_label, self.model._meta.verbose_name))
            if isinstance(datatables_class, str):
                try:
                    datatables_class = import_string(datatables_class)
                except ImportError:
                    raise ImproperlyConfigured('Error in datatables configured in {}:{}'
                                               .format(self.model._meta.app_label, self.model._meta.verbose_name))
            if not issubclass(datatables_class, ModelDataTable):
                raise ImproperlyConfigured('Improperly configured datatables_class attr in {}:{}'
                                           .format(self.model._meta.app_label, self.model._meta.verbose_name))
            self.dt_config = datatables_class
        return False

    def get_related_entity_config(self):
        # 注意这里要使用self.main_entity
        # 因为这个设置发生在self.process_session()之后，
        # 并且是要从main_entity这个model中获取信息
        related_entity_config = self.related_entity_config or getattr(self.main_entity, 'related_entity_config', None)
        if related_entity_config is None:
            raise ImproperlyConfigured('Must configure related entity config for model: {}:{}'
                                       .format(self.model._meta.app_label, self.model._meta.verbose_name))
        if not isinstance(related_entity_config, dict):
            raise ImproperlyConfigured('Related entity config for {}:{} must be a dict'
                                       .format(self.model._meta.app_label, self.model._meta.verbose_name))
        return related_entity_config

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)


class RelatedEntityView(RelatedEntityConstructMixin, generic.UpdateView):
    def get(self, request, *args, **kwargs):
        if self.construct_related_entity():
            return HttpResponseRedirect(request.path_info)
        if self.is_related():
            if self.action == 'create':
                # 还需要设置self.initial等属性
                # 以及设置fields
                self.object = None
                return self.render_to_response(self.get_context_data(dt_config=None))
            else:
                self.object = None
                if request.is_ajax():
                    return self.render_to_json_response(self.get_json_context_data(request.GET))
                else:
                    # 注意：要设置form关键字参数，因为get_context_data()调用链
                    # 在调用到FormMixin时，如果没有设置这个参数，会自动生成form实例
                    # 这个在list的情况下是不需要的
                    return self.render_to_response(self.get_context_data(form=None))
        else:
            self.object = self.get_object()
            return self.render_to_response(self.get_context_data(dt_config=None))

    def post(self, request, *args, **kwargs):
        self.construct_related_entity()
        if not self.is_related() or self.action == 'create':
            if self.is_related():
                self.object = None
                self.success_url = '{}?action=list'.format(self.request.path_info)
            else:
                self.object = self.get_object()
                self.success_url = self.request.path_info
            form = self.get_form()
            if form.is_valid():
                return self.form_valid(form)
            else:
                return self.render_to_response(self.get_context_data(form=form, dt_config=None))
        elif not self.is_related():

            return super().post(request, *args, **kwargs)
        else:
            return self.get(request, *args, **kwargs)
