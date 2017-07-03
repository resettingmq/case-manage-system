from django.test import TestCase
from base.models import Profile

# Create your tests here.


class ProfileModelTestCase(TestCase):

    def test_profile_created_when_user_created(self):
        from django.contrib.auth.models import User
        user = User.objects.create_user(
            'test_user',
            'test_user@test.com',
            'testpassword',
        )
        profile = Profile.objects.get(user_id=user.id)
        self.assertIsNotNone(profile)
