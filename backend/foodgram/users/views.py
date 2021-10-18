from django.contrib.auth import update_session_auth_hash

from djoser.conf import settings
from djoser import utils
from djoser.compat import get_user_email
from djoser.views import UserViewSet as DjoserUserViewSet

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response


class UserViewSet(DjoserUserViewSet):
    """ overwrote djoser viewset. Added status and pass data in response """

    @action(["post"], detail=False)
    def set_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.request.user.set_password(serializer.data["new_password"])
        self.request.user.save()

        if settings.PASSWORD_CHANGED_EMAIL_CONFIRMATION:
            context = {"user": self.request.user}
            to = [get_user_email(self.request.user)]
            settings.EMAIL.password_changed_confirmation(self.request, context).send(to)

        if settings.LOGOUT_ON_PASSWORD_CHANGE:
            utils.logout_user(self.request)
        elif settings.CREATE_SESSION_ON_LOGIN:
            update_session_auth_hash(self.request, self.request.user)
        new_pass_data = {
                "new_password": serializer.data["new_password"],
                "current_password": serializer.data["new_password"]
        }
        return Response(new_pass_data, status=status.HTTP_201_CREATED)