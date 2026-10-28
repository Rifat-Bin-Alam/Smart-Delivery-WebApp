from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q


class EmailOrUsernameModelBackend(ModelBackend):
    """
    Authentication backend that allows users to authenticate using either
    their email address or their username.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD) or kwargs.get('email')

        if not username or not password:
            return None

        username = str(username).strip()
        try:
            # Match by email (case-insensitive) or username (case-insensitive)
            user = UserModel.objects.filter(
                Q(email__iexact=username) | Q(username__iexact=username)
            ).first()

            if user and user.check_password(password) and self.user_can_authenticate(user):
                return user
        except Exception:
            return None

        return None
