# -*- coding: utf-8 -*-

from decimal import Decimal

from django.test import TestCase, TransactionTestCase
from django.db import transaction

from sale.models import Receivable


class ReceivableTableTriggerTestCase(TransactionTestCase):

    def test_insert_unsettled_amount_set(self):
        amount = Decimal('1000.15')
        with transaction.atomic():
            rv = Receivable.objects.create(amount=amount)
        result = Receivable.objects.get(pk=rv.pk)
        print(result.amount)
        print(result.unsettled_amount)
        self.assertEqual(result.unsettled_amount, amount)
