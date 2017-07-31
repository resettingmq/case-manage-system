from functools import reduce
from collections import OrderedDict
from django.views import generic
from django.http import JsonResponse, HttpResponseRedirect
from django.core.exceptions import ImproperlyConfigured, SuspiciousOperation
from django.apps import apps
from django.utils.module_loading import import_string
from django.db.models import Q
from django.forms.models import ModelFormMetaclass

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


class ModelDataTablesMixin(DataTablesMixin):
    """
    根据self.model中的相关属性配置DataTablesMixin属性
    注意是动态生成，每次请求都应该被调用，
    包括ajax请求
    """
    def config_datatables_from_model(self, dt_config=None):
        if self.dt_config is not None:
            return
        try:
            datatables_class = self.model.datatables_class
        except AttributeError:
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

    def get_context_data(self, **kwargs):
        # 注意：这里也需要对kwargs中的dt_config参数进行判断
        # 这样才能够与DatatablesMixin统一
        # 同时在子类中才能够控制self.dt_config的生成获取
        if 'dt_config' not in kwargs:
            self.config_datatables_from_model()
        return super().get_context_data(**kwargs)

    def get_json_context_data(self, *args, **kwargs):
        self.config_datatables_from_model()
        return super().get_json_context_data(*args, **kwargs)


class DataTablesListView(ModelDataTablesMixin, generic.ListView):

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            # if not self.dt_config.dt_serverSide:
                return self.render_to_json_response(self.get_json_context_data(request.GET))
        return super().get(request, *args, **kwargs)


class InfoboxMixin:
    view_name = None
    infobox_list = None
    extra_query_object = None

    def get_infobox_list(self):
        return self.infobox_list

    def get_infobox_dict(self):
        infobox_list = self.get_infobox_list()
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

            extra_query_object = self.get_extra_query_object(model_name=infobox_name, model=model)
            count = model._default_manager.filter(extra_query_object).count()
            ret.append((infobox_name, {'related_entity_name': infobox_name, 'count': count}))

        return OrderedDict(ret)

    def get_extra_query_object(self, *args, **kwargs):
        if self.extra_query_object is None:
            return Q()

    def get_context_data(self, **kwargs):
        kwargs.update(infobox_dict=self.get_infobox_dict())
        return super().get_context_data(**kwargs)


class ConfiguredModelFormMixin:
    """
    根据Model中的属性和函数配置FormMixin中相关属性
    依赖于FormMixin
    """
    def config_form_from_model(self):
        try:
            modelform_class = self.model.modelform_class
        except AttributeError:
            modelform_class = None
        if isinstance(modelform_class, str):
            try:
                modelform_class = import_string(modelform_class)
            except ImportError:
                pass
        if isinstance(modelform_class, ModelFormMetaclass):
            self.form_class = modelform_class
            # 设置self.form_class成功之后，self.fields将失效
            # 避免产生同时设置form_class和fields的错误
            self.fields = None
            return
        try:
            self.fields = self.model.form_fields
        except AttributeError:
            pass
        if self.fields is None and self.form_class is None:
            raise ImproperlyConfigured('form_class or fields are not properly configured for model {}:{}'
                                       .format(self.model._meta.app_label, self.model._meta.verbose_name))

    def get_form_class(self):
        """
        : 重写父类中的get_form_class(),在调用父类方法之前，设置好form相关属性
        :return: 
        """
        if not self.form_class:
            self.config_form_from_model()
        return super().get_form_class()


class RelatedEntityConstructMixin(ConfiguredModelFormMixin, InfoboxMixin, ModelDataTablesMixin, generic.list.MultipleObjectMixin):
    main_entity = None
    main_object = None
    main_entity_name = None
    current_entity_name = None
    action = None
    # config dict 存储与main_entity相关model的信息
    related_entity_config = None
    # 用于指定detail页面坐上角显示的概要信息
    detail_info = {'title': 'name'}

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
                # del self.request.session['current_entity_name']
                del self.request.session[self.main_entity_name]
                del self.request.session['action']
            except KeyError:
                pass
            return True
        current_entity_name = self.request.GET.get('current', '')
        action = self.request.GET.get('action', None)
        if current_entity_name:
            try:
                apps.get_model(current_entity_name)
                self.request.session[self.main_entity_name] = current_entity_name
                self.request.session['action'] = self.request.GET.get('action', 'list')
            except (LookupError, ValueError):
                return False
            return True
        if action:
            self.request.session['action'] = action
            return True
        return False

    def process_session(self):
        """
        : 获取session中的related_entity_name, 以及action
        : 并根据related_entity_str设置self.model
        :return: 
        """
        current_entity_name = self.request.session.get(self.main_entity_name, '')
        try:
            self.model = apps.get_model(current_entity_name)
            self.current_entity_name = current_entity_name
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
        self.main_entity_name = self.model._meta.label
        self.main_entity = self.model
        if self.process_query_args():
            return True
        self.main_object = self.get_object()
        self.process_session()
        # 设置infobox相关属性
        self.infobox_list = self.get_related_entity_config().keys()
        # 设置object_list，因为继承了MultipleObjectMixin，
        # 在它的get_context_data()中，读取了这个值
        # 这个情况比较诡异，虽然MultipleObjectMixin中可以根据关键字参数设置object_list
        # 但是它用到了pop('object_list', self.object_list)
        # 即便是字典中有'object_list'这个键，还是会evaluate self.object_list!!!
        self.object_list = self.get_queryset()

        return False

    def get_related_entity_config(self, model_name=None):
        # 注意这里要使用self.main_entity
        # 因为这个设置发生在self.process_session()之后，
        # 并且是要从main_entity这个model中获取信息
        # 缓存结果到self.related_entity_config
        if self.related_entity_config is not None:
            related_entity_config = self.related_entity_config
        else:
            try:
                related_entity_config = self.main_entity.get_related_entity_config()
            except AttributeError:
                related_entity_config = None
            if related_entity_config is None:
                raise ImproperlyConfigured('Must configure related entity config for model: {}:{}'
                                           .format(self.main_entity._meta.app_label, self.main_entity._meta.verbose_name))
            if not isinstance(related_entity_config, dict):
                raise ImproperlyConfigured('Related entity config for {}:{} must be a dict'
                                           .format(self.main_entity._meta.app_label, self.main_entity._meta.verbose_name))
            self.related_entity_config = related_entity_config
        if model_name is not None:
            return related_entity_config.get(model_name)

        return related_entity_config

    def get_related_query_path(self, model_name):
        """
        : 获取model_name指向model到self.main_model的关系路径
        :param model_name: 
        :return: str, 一般用于构造对model_name指向model的查询条件
        """
        related_entity_config = self.get_related_entity_config()
        try:
            query_path = related_entity_config[model_name]['query_path']
        except KeyError:
            # 发生KeyError，有可能是其他RelatedEntityView设置了related_model
            # 而这个related_model在当前model中不存在
            raise ImproperlyConfigured('Related entity config error: {} to {}:{}'
                .format(
                model_name,
                self.main_entity._meta.app_label,
                self.main_entity._meta.verbose_name
            ))
        if not isinstance(query_path, str):
            raise ValueError('query_path for {} must be a str'.format(model_name))
        return query_path

    def get_queryset(self):
        """
        : 在DatatableMixin中使用
        :return: 
        """
        queryset = super().get_queryset()
        if not self.is_related():
            return queryset
        query_path = self.get_related_query_path(self.current_entity_name)
        return queryset.filter(**{query_path: self.main_object})

    def get_extra_query_object(self, model_name, model):
        """
        : 继承自InfoboxMixin
        :param model_name: related app_label.model_name形式
        :param model: model class
        :return: Q object
        """
        query_path = self.get_related_query_path(model_name)
        return Q(**{query_path: self.main_object})

    def get_initial(self):
        """
        : 在FormMixin中被定义, 在get_form_kwargs()中被调用
        :return: 
        """
        if not self.is_related():
            return super().get_initial()
        initial = {}
        query_path = self.get_related_query_path(self.current_entity_name)
        try:
            field_name, query_string = query_path.split('__', 1)
        except ValueError:
            initial[query_path] = self.main_object
        else:
            field_related_model = self.model._meta.get_field(field_name).related_model
            initial[field_name] = field_related_model._default_manager.filter(**{query_string: self.main_object})
        return initial

    def get_detail_info_context(self):
        try:
            detail_info = self.main_object.get_detail_info()
        except AttributeError:
            detail_info = None
        if detail_info is not None:
            return detail_info
        detail_info = {}
        try:
            detail_info['title'] = getattr(self.main_object, self.detail_info['title'], None)
        except KeyError:
            detail_info['title'] = None
        try:
            detail_info['sub_title'] = getattr(self.main_object, self.detail_info['sub_title'], None)
        except KeyError:
            pass
        if 'desc' in self.detail_info:
            detail_info['desc'] = {}
            for k, v in self.detail_info.get('desc', {}).items():
                detail_info['desc'][k] = getattr(self.main_object, v, None)

        return detail_info

    def get_related_data_context(self):
        related_config = self.get_related_entity_config(self.current_entity_name)
        try:
            verbose_name = related_config['verbose_name']
        except (TypeError, KeyError):
            return None
        related_data = {'related_entity_verbose_name': verbose_name}
        return related_data

    def get_context_data(self, **kwargs):
        kwargs['detail_info'] = self.get_detail_info_context()
        kwargs['related_data'] = self.get_related_data_context()
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
                # 消除Main model view类属性form_class的影响
                # 以便使得能够重新加载related model中定义的modelform class
                self.form_class = None
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
                # 消除Main model view类属性form_class的影响
                # 以便使得能够重新加载related model中定义的modelform class
                self.form_class = None
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
