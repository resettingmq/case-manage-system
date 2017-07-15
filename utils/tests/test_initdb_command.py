# -*- coding: utf-8 -*-

from django.test import TestCase, TransactionTestCase
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import transaction


class InitdbCommandTestCase(TransactionTestCase):
    def test_initdb_command_registered(self):
        try:
            call_command('initdb', 'some_app')
        except CommandError as e:
            if 'Unknown command' in e.args[0]:
                self.fail('command initdb not registered')

    def test_accept_app_label_positional_argument(self):
        try:
            call_command('initdb', 'some_app')
        except CommandError as e:
            if 'unrecognized arguments' in e.args[0]:
                self.fail('command initdb does not accept app_label argument')

    def test_app_label_argument_is_optional(self):
        try:
            call_command('initdb', )
        except CommandError as e:
            if 'the following arguments are required: app_label' in e.args[0]:
                self.fail('command initdb app_label should be optional')
        except AttributeError:
            pass

    def test_raise_command_error_when_app_label_not_found(self):
        with self.assertRaisesRegexp(CommandError, 'app .+ not found'):
            call_command('initdb', 'not_existed_app')

    def test_accept_model_name_positional_argument(self):
        try:
            call_command('initdb', 'some_app', 'some_model')
        except CommandError as e:
            if 'unrecognized arguments' in e.args[0]:
                self.fail('command initdb does not accept model_name argument')

    # def test_model_name_argument_is_optional(self):
    #     # 这个测试变得没有意义，
    #     # 不会被触发
    #     # 因为前面的位置参数为可选，之后的参数是必须的情况下，
    #     # 他们之间的位置会发生变化
    #     # 必须的位置参数永远排在可选位置参数之后
    #     try:
    #         call_command('initdb', 'some_app', )
    #     except CommandError as e:
    #         if 'the following arguments are required: model_name' in e.args[0]:
    #             self.fail('command initdb model_name should be optional')

    def test_raise_command_error_when_model_name_not_found(self):
        # 这个测试里需要给定一个正确的app_label
        # 因为app_label的判断排在model_name之前，
        # 如果app_label不正确，就不会出发model_name相关的异常
        with self.assertRaisesRegexp(CommandError, 'model .+ not found'):
            call_command('initdb', 'auth', 'not_existe_model')

    def test_properly_polulate_data_without_app_label(self):
        from base.models import Client
        from case.models import Case

        call_command('initdb')

        self.assertNotEqual(Client.objects.count(), 0)
        self.assertNotEqual(Case.objects.count(), 0)

    def test_properly_polulate_data_with_only_app_label(self):
        from base.models import Client
        from case.models import Case, Contract

        call_command('initdb', 'case')

        self.assertNotEqual(Case.objects.count(), 0)
        self.assertNotEqual(Contract.objects.count(), 0)
        self.assertEqual(Client.objects.count(), 0)

    def test_properly_populate_data_with_app_label_and_model_name(self):
        from base.models import Client
        from case.models import Case, Contract
        # 需要添加一个Client，因为Case数据中有到Client的外键

        call_command('initdb', 'case', 'case')

        self.assertNotEqual(Case.objects.count(), 0)
        self.assertEqual(Client.objects.count(), 0)
        self.assertEqual(Contract.objects.count(), 0)
