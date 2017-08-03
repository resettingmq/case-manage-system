# -*- coding: utf-8 -*-

from django.test import TestCase, RequestFactory
from utils.views import RelatedEntityView
from base.models import Client


class ClientRelatedEntityView(RelatedEntityView):
    model = Client
    fields = ['name']


class RelatedEntityViewTestCase(TestCase):
    def setUp(self):
        self.client = Client.objects.create(name='test client')
        self.factory = RequestFactory()

    def test_redirect_response(self):
        pass

    def test_valid_query_args_set_session(self):
        req = self.factory.get('/client/1?current=case.case?action=list')
        res = ClientRelatedEntityView.as_view()(req, pk=self.client.pk)
        print(res)
        self.assertTrue(res.has_header('set-cookie'))
