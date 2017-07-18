# -*- coding: utf-8 -*-

import re
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.decorators import login_required

LOGIN_REQUIRED_EXCEPTIONS = [re.compile(settings.LOGIN_URL.strip('/'))]
if hasattr(settings, 'LOGIN_REQUIRED_EXCEPTIONS') and \
        isinstance(settings.LOGIN_REQUIRED_EXCEPTIONS, list):
    LOGIN_REQUIRED_EXCEPTIONS += [re.compile(exc) for exc in settings.LOGIN_REQUIRED_EXCEPTIONS]


class LoginRequiredMiddleware(MiddlewareMixin):

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.user.is_authenticated():
            return None

        path_info = request.path_info.strip('/')
        if not any(regex.match(path_info) for regex in LOGIN_REQUIRED_EXCEPTIONS):
            return login_required(view_func)(request, *view_args, **view_kwargs)

        return None
