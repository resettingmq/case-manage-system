from functools import reduce
from collections import OrderedDict
from django.views import generic
from django.http import JsonResponse, HttpResponseRedirect
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.apps import apps
from django.utils.module_loading import import_string
from django.db.models import Q
from django.forms.models import ModelFormMetaclass
from django.forms.utils import ErrorList
from django.contrib import messages

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
    enabled_objects_manager = 'enabled_objects'

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

    def process_http_queryset(self, queryset):
        pass

    def get_json_context_data(self, http_queryset=None):
        """
        : 依赖于其他class的get_queryset()方法
        : 包含了数据获取，处理的逻辑
        :return: dict
        """
        json_context = {}

        # 用于控制是否返回disabled项
        # 要求model中定义了enabled_objects Manager
        # 因为初始请求的query args中不存在show_disabled参数
        # 为了保证默认不显示disabled的项目，这里要将get的默认值设为'0'
        show_disabled = http_queryset.get('show_disabled', '0')
        if show_disabled == '0':
            # 如果没有找到，则self.queryset为None
            # 这样在下面的执行中会默认使用_default_manager
            # 所以可以 避免 没有enabled/disabled区分的情况下结果不正确
            self.queryset = getattr(self.model, self.enabled_objects_manager, None)
        elif show_disabled == '1':
            self.queryset = self.model._default_manager

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
        # 将count的查询作用在model.enabled_objects上
        # 只显示enabled项
        # 依赖于model定义了enabled_objects Manager
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
        for infobox_name, infobox_value in infobox_list.items():
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
            count = model.enabled_objects.filter(extra_query_object).count()
            t_name = infobox_value.get('t_name')
            ret.append((infobox_name, {'related_entity_name': infobox_name, 'count': count, 't_name': t_name}))

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


class FormMessageMixin:
    """
    : 用于将Form中的成功/失败信息添加到messages中
    """
    def form_invalid(self, form):
        for field, errors in form.errors.items():
            messages.error(
                self.request,
                errors
            )
        return super().form_invalid(form)

    def form_valid(self, form):
        action = '修改' if form.instance.pk else '创建'
        entity_verbose_name = form.instance._meta.verbose_name
        message = '{}{}成功'.format(
            action,
            entity_verbose_name,
        )
        messages.success(
            self.request,
            message
        )
        return super().form_valid(form)


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
    # 用于指定delete(disable)页面url
    delete_url = None
    # 用于指定main entity支持的额外action
    main_entity_extra_action = []

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
            except KeyError:
                pass
            try:
                del self.request.session['action']
            except KeyError:
                pass
            return True

        current_entity_name = self.request.GET.get('current', '')
        action = self.request.GET.get('action', None)
        if current_entity_name:
            related_entity_config = self.get_related_entity_config()
            if current_entity_name not in related_entity_config:
                # 如果GET query args中指定的current_entity_name不存在于related_entity_config中
                # 则不设置session直接发生跳转。
                return True
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
        related_entity_config = self.get_related_entity_config()
        if current_entity_name not in related_entity_config:
            # 如果session中的current_entity_name不存在于related_entity_config中
            # 则不设置entity context（保持main_model）。
            # self.current_entity_name和self.action为None
            # 如果不这样做，在某些场景下会出现related_entity不存在的情况，即使是按main_model为key来存储related_entity
            # 例如某些client(agent)对应agent subcase，某些client(非agent)不对应angent subcase
            action = self.request.session.get('action', None)
            if action in self.main_entity_extra_action:
                # 增加这部分，使得能够在main entity上支持其它的action
                # 便于扩展
                self.action = action
            return True
        try:
            # 尝试更改当前view的model context
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
        self.main_object = self.get_object()
        if self.process_query_args():
            return True
        self.process_session()
        # 设置infobox相关属性
        self.infobox_list = self.get_related_entity_config()
        # 设置object_list，因为继承了MultipleObjectMixin，
        # 在它的get_context_data()中，读取了这个值
        # 这个情况比较诡异，虽然MultipleObjectMixin中可以根据关键字参数设置object_list
        # 但是它用到了pop('object_list', self.object_list)
        # 即便是字典中有'object_list'这个键，还是会evaluate self.object_list!!!
        self.object_list = self.get_queryset()

        return False

    def form_invalid(self, form):
        """
        : 重写FormMixin中的form_invalid()方法
        : 因为在form context(create/update)中，context_data中的dt_config不存在，
        : 需要通过get_context_data()方法的dt_config=None关键字参数控制
        : 所以这里需要重写form_invalid()方法
        """
        return self.render_to_response(self.get_context_data(form=form, dt_config=None))

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

            # 复制related_entity_config，避免下面的pop()修改View/Model中设置的类属性
            self.related_entity_config = dict(related_entity_config)
            _sentinel = object()
            for related_name, related_config in related_entity_config.items():
                related_when = related_config.get('related_when')
                if related_when is None:
                    continue
                for key, val in related_when.items():
                    obj_val = getattr(self.main_object, key, _sentinel)
                    if val != obj_val:
                        self.related_entity_config.pop(related_name)
                        break
            related_entity_config = self.related_entity_config

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

    def get_form(self):
        """
        : 在FormMixin中被定义
        : 重写用于设置ModelChoiceField的queryset范围
        : 同时，在非related的情况下，表单提交按钮显示为‘修改’，默认为‘增加’
        :param form_class: 
        :return: form instance
        """
        if not self.is_related():
            form = super().get_form()
            form.submit_button_value = '修改'
            if not self.object.enabled:
                # 如果object状态为disabled
                # 则将form中所有field设置为disabled
                for field in form.fields.values():
                    field.disabled = True
            return form

        # 强制在form实例化外生成self.object
        # 并在self.object上设置相关初始值
        # 弃用了在get_initial()中设置form的初始值
        # 这是为了在子类重写__init__()方法的时候，能够统一使用form.instance
        # 能够这样做是因为related-form只会是create form，对应的instance只能是新对象

        # 从get_related_form()提前到get_form()方法中实例化model
        # 这样就能够在子类重写get_related_form()时使用self.object，例如设置初始值
        self.object = self.model()

        return self.get_related_form()

    def get_related_form(self):
        """
        : 设置相关的初始值到self.object
        : 重写用于设置ModelChoiceField的queryset范围
        :return: 
        """
        query_path = self.get_related_query_path(self.current_entity_name)
        try:
            field_name, query_string = query_path.split('__', 1)
        except ValueError:
            setattr(self.object, query_path, self.main_object)
        form = super().get_form()

        # 设置form相关field的queryset
        try:
            field_name, query_string = query_path.split('__', 1)
        except ValueError:
            field = form.fields.get(query_path)
            if field is not None:
                field.queryset = field.queryset.filter(pk=self.main_object.pk)
        else:
            field = form.fields.get(field_name)
            if field is not None:
                queryset = field.queryset
                field.queryset = queryset.filter(**{query_string: self.main_object})
        return form

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
        """
        : 生成在template中需要显示的related entity信息
        : 最终会添加到template context data中
        :return: dict，如果currenct_entity_name为None，则返回None
        """
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
        kwargs['deletion_url'] = self.get_deletion_url()
        kwargs['main_object'] = self.main_object
        return super().get_context_data(**kwargs)

    def get_deletion_url(self):
        """
        : 用于获取delete_url
        : 依赖于self.main_object
        : 依赖于self.main_object.get_delete_url()
        : 返回值会被添加到context_data['delete_url']中
        :return: url or None
        """
        if self.is_related():
            # 当curr entity为related entity的时候
            # 不显示delete按钮
            return None
        if self.delete_url:
            url = self.delete_url.format(**self.object.__dict__)
        else:
            try:
                url = self.main_object.get_deletion_url()
            except AttributeError:
                url = None
        return url

    def handle_get(self, request, *args, **kwargs):
        # 处理重定向后的get请求
        # 增加这个方法的目的是在子类中可以重写这个方法
        # 便于扩展
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

    def handle_post(self, request, *args, **kwargs):
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
                return self.form_invalid(form)
        elif not self.is_related():

            return super().post(request, *args, **kwargs)
        else:
            return self.get(request, *args, **kwargs)


class RelatedEntityView(FormMessageMixin, RelatedEntityConstructMixin, generic.UpdateView):
    def get(self, request, *args, **kwargs):
        if self.construct_related_entity():
            return HttpResponseRedirect(request.path_info)
        return self.handle_get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.construct_related_entity()
        return self.handle_post(request, *args, **kwargs)


class DisablementMixin:
    """
    : 处理post()请求，将指定object禁用
    : 依赖与SingleObjectMixin等类的get_object()方法
    """
    success_url = None
    error = None

    def process_disable(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.clean()

        if self.error:
            redirect_url = request.META['HTTP_REFERER']
            messages.error(
                request,
                self.error
            )
        else:
            redirect_url = self.get_success_url()
            self.disable()
            entity_verbose = self.object._meta.verbose_name
            messages.success(
                request,
                '成功删除{}: {}'.format(entity_verbose, self.object)
            )

        return HttpResponseRedirect(redirect_url)

    def disable(self):
        self.object.enabled = False
        self.object.save()

    def validate(self):
        if not hasattr(self.object, 'enabled'):
            raise ValidationError(
                '该对象不能被删除',
                code='invalid'
            )

    def clean(self):
        try:
            self.validate()
        except ValidationError as e:
            self.error = ErrorList(
                initlist=e.error_list,
                error_class='nonfield'
            )

    def get_success_url(self):
        if self.success_url:
            success_url = self.success_url.format(**self.object.__dict__)
        else:
            try:
                success_url = self.object.get_deletion_success_url()
            except AttributeError:
                raise ImproperlyConfigured(
                    "No URL to redirect to. Provide a success_url.")
        return success_url


class DisablementView(DisablementMixin, generic.detail.SingleObjectMixin,
                      generic.View):
    """
    : 直接继承自View，使得仅支持POST方法
    """
    def post(self, request, *args, **kwargs):
        return self.process_disable(request, *args, **kwargs)
