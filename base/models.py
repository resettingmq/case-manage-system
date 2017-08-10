import os
from collections import OrderedDict

from django.db import models
from django.db.models.signals import post_save
from django.db.utils import IntegrityError
from django.urls import reverse
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.utils import timezone
from django.conf import settings

BASE_DIR = settings.BASE_DIR

# Create your models here.


class EnabledEntityManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(enabled=True)


class Profile(models.Model):
    avatar_hash = models.CharField(max_length=32, null=True)
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)

    def __str__(self):
        return '{}-profile'.format(self.user.username)

    def gravatar(self, size=100, default='identicon', rating='g'):
        url = 'http://www.gravatar.com/avatar'
        if self.avatar_hash is None:
            email = self.user.email or 'anonymous@gmail.com'
            import hashlib
            self.avatar_hash = hashlib.md5(email.encode('utf-8')).hexdigest()
            self.save()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url,
            hash=self.avatar_hash,
            size=size,
            default=default,
            rating=rating
        )


@receiver(post_save, sender=User)
def save_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()


class CommonFieldMixin(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    enabled = models.BooleanField(default=True)

    class Meta:
        abstract = True


class DescriptionFieldMixin(models.Model):
    desc = models.TextField('备注', null=True, blank=True)

    class Meta:
        abstract = True


class FakerMixin:
    # todo:
    # 1. one to one relationship: 有添加重复外键的可能
    faker_fields = None
    data_path = None

    @classmethod
    def populate(cls, count=100, locale='en_US'):
        if cls.data_path:
            import json
            items = json.load(open(cls.data_path))
            for item in items:
                try:
                    cls.objects.create(**item)
                except IntegrityError:
                    pass
            return
        if not cls.faker_fields:
            raise ValueError('You must specify faker_fiedls or data_path.')
        for fake_type in cls.faker_fields.values():
            if isinstance(fake_type, str):
                continue
            if isinstance(fake_type, type) and issubclass(fake_type, models.Model):
                continue
            raise ValueError('fake type must be a str or a Model class inherited from models.Model')
        try:
            import faker
        except ImportError:
            print('Faker is not installed')
        else:
            fake = faker.Factory.create(locale)
            fake_objs = []
            for i in range(count):
                data = {}

                for field_name, fake_type in cls.faker_fields.items():
                    is_model_class = not isinstance(fake_type, str)
                    if is_model_class or '.' in fake_type:
                        from random import randint
                        if is_model_class:
                            related_model = fake_type
                        else:
                            from django.utils.module_loading import import_string
                            try:
                                related_model = import_string(fake_type)
                            except ImportError:
                                raise
                        related_obj_count = related_model.objects.count()
                        if related_obj_count == 0:
                            data[field_name] = None
                        else:
                            data[field_name] = related_model.objects.all()[randint(0, related_obj_count-1)]
                    else:
                        data[field_name] = getattr(fake, fake_type)()
                try:
                    cls.objects.create(**data)
                except IntegrityError:
                    continue
            #     fake_objs.append(cls(**data))
            # cls.objects.bulk_create(fake_objs)


class Continent(FakerMixin, CommonFieldMixin):
    id = models.CharField(max_length=5, primary_key=True)
    name_chs = models.CharField(max_length=20, db_index=True)
    name_en = models.CharField(max_length=20, db_index=True)

    objects = models.Manager()
    enabled_objects = EnabledEntityManager()

    data_path = os.path.join(BASE_DIR, 'data/continent.json')

    class Meta:
        verbose_name = '洲'
        verbose_name_plural = '洲'

    def __str__(self):
        return '{c.id}-{c.name_chs}'.format(c=self)


class Country(FakerMixin, CommonFieldMixin):
    id = models.CharField(max_length=2, primary_key=True)
    name_chs = models.CharField('中文名', max_length=50, null=True, blank=True)
    name_en_short = models.CharField(max_length=50)
    name_en_long = models.CharField(max_length=100, null=True, blank=True)
    calling_code = models.CharField(max_length=50)
    iso_code = models.CharField(max_length=5)
    is_eu = models.BooleanField(default=False)
    is_madrid = models.BooleanField(default=False)
    is_oapi = models.BooleanField(default=False)

    continent = models.ForeignKey(Continent, null=True, blank=True)

    objects = models.Manager()
    enabled_objects = EnabledEntityManager()

    data_path = os.path.join(BASE_DIR, 'data/country.json')

    class Meta:
        verbose_name = '国家'
        verbose_name_plural = '国家'

    def __str__(self):
        return '{c.id}-{c.name_en_short}-{c.name_chs}'.format(c=self)


class Currency(FakerMixin, CommonFieldMixin):
    id = models.CharField(max_length=5, primary_key=True)
    name_chs = models.CharField(max_length=50)
    name_en = models.CharField(max_length=50)
    symbol = models.CharField(max_length=5, null=True, blank=True)

    objects = models.Manager()
    enabled_objects = EnabledEntityManager()

    data_path = os.path.join(BASE_DIR, 'data/currency.json')

    class Meta:
        verbose_name = '货币'
        verbose_name_plural = '货币'

    def __str__(self):
        return '{c.id}-{c.name_chs}-{c.name_en}'.format(c=self)


class Owner(FakerMixin, CommonFieldMixin, DescriptionFieldMixin):
    name = models.CharField('名称', max_length=100)

    objects = models.Manager()
    enabled_objects = EnabledEntityManager()

    class Meta:
        verbose_name = '所属部门'
        verbose_name_plural = '所属部门'

    data_path = os.path.join(BASE_DIR, 'data/owner.json')

    def __str__(self):
        return self.name


class Client(FakerMixin, CommonFieldMixin, DescriptionFieldMixin):
    name = models.CharField('客户名称', max_length=100)
    is_agent = models.BooleanField('是否代理', default=False)
    tel = models.CharField('电话', max_length=30, null=True, blank=True)
    mobile = models.CharField('移动电话', max_length=30, null=True, blank=True)
    fax = models.CharField('传真', max_length=30, null=True, blank=True)
    state = models.CharField('省/地区', max_length=100, null=True, blank=True)
    city = models.CharField('城市', max_length=100, null=True, blank=True)
    address = models.CharField('地址', max_length=200, null=True, blank=True)
    postal_code = models.CharField('邮编', max_length=20, null=True, blank=True)

    currency = models.ForeignKey(
        Currency,
        verbose_name='常用货币',
        on_delete=models.SET_NULL,
        null=True
    )
    country = models.ForeignKey(
        Country,
        verbose_name='所在国家',
        on_delete=models.SET_NULL,
        null=True
    )

    objects = models.Manager()
    enabled_objects = EnabledEntityManager()

    modelform_class = 'base.forms.ClientModelForm'
    datatables_class = 'base.datatables.ClientDataTable'
    related_entity_config = {
        'case.case': {
            'query_path': 'client',
            'verbose_name': '案件信息'
        },
        'case.subcase': {
            'related_when': {'is_agent': True},
            'query_path': 'agent',
            'verbose_name': '代理分案信息'
        }
    }

    faker_fields = {
        'name': 'company',
        'is_agent': 'pybool',
        'tel': 'phone_number',
        'mobile': 'phone_number',
        'fax': 'phone_number',
        'state': 'state',
        'city': 'city',
        'address': 'street_address',
        'postal_code': 'postcode',
        'currency': Currency,
        'country': 'base.models.Country',
    }

    class Meta:
        verbose_name = '客户/代理'
        verbose_name_plural = '客户/代理'

    def __str__(self):
        return '{c.name}'.format(c=self)

    def get_absolute_url(self):
        return reverse('client:detail', kwargs={'client_id': self.pk})

    def get_deletion_url(self):
        return reverse('client:disable', kwargs={'client_id': self.id})

    def get_deletion_success_url(self):
        return reverse('client:detail', kwargs={'client_id': self.id})

    @classmethod
    def get_related_entity_config(cls):
        if cls.related_entity_config is not None:
            return cls.related_entity_config

    def get_detail_info(self):
        detail_info = {}
        desc = OrderedDict()
        detail_info['title'] = self.name
        detail_info['sub_title'] = self.country.name_chs
        desc['电话'] = self.tel or '没有设置'
        desc['移动电话'] = self.mobile or '没有设置'
        desc['传真'] = self.fax or '没有设置'
        detail_info['desc'] = desc
        detail_info['enabled'] = self.enabled

        return detail_info
