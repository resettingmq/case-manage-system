from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver

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
