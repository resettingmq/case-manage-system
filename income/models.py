from django.db import models

from base.models import CommonFieldMixin, DescriptionFieldMixin, FakerMixin

# Create your models here.


class Deposit(CommonFieldMixin, DescriptionFieldMixin):
    amount = models.DecimalField('预收款总额', max_digits=10, decimal_places=2)
    balance = models.DecimalField('预收款余额', max_digits=10, decimal_places=2,
                                  null=True, blank=False)
    received_date = models.DateField('收到日期')

    client = models.ForeignKey(
        'base.Client',
        verbose_name='客户',
        on_delete=models.SET_NULL,
        null=True
    )
    currency = models.ForeignKey(
        'base.Currency',
        verbose_name='货币',
        on_delete=models.SET_NULL,
        null=True
    )
