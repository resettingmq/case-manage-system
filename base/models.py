import os

from django.db import models
from django.db.models.signals import post_save
from django.db.utils import IntegrityError
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.utils import timezone
from django.conf import settings

BASE_DIR = settings.BASE_DIR

# Create your models here.


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


class Continent(CommonFieldMixin):
    id = models.CharField(max_length=5, primary_key=True)
    name_chs = models.CharField(max_length=20, db_index=True)
    name_en = models.CharField(max_length=20, db_index=True)

    data_path = os.path.join(BASE_DIR, 'data/continent.json')

    def __str__(self):
        return '{c.id}-{c.name_chs}'.format(c=self)

    @classmethod
    def populate(cls):
        import json
        continents = json.load(open(cls.data_path))
        for c in continents:
            try:
                cls.objects.create(**c)
            except IntegrityError:
                pass
