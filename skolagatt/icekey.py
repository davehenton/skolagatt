from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User

class IcekeyAuhentication(object):
    def authenticate(self, username=None, password=None):
	try:
		user = User.objects.get(username=username)
		if user.check_password(password):
			return user
	except User.DoesNotExist:
		user = User(username=username, password=password)
		user.is_staff = True
		user.is_superuser = True
		user.save()
		return user
	return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
