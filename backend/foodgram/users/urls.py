from rest_framework.routers import DefaultRouter

from django.urls import include, path

from .views import UserViewSet

router = DefaultRouter()

router.register(r'users', UserViewSet, basename='UserViewSet')


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken'))
]

