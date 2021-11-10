from django.contrib import admin
from .models import User, Follow


class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'password', 'first_name')


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')


admin.site.register(User, UserAdmin)
admin.site.register(Follow, FollowAdmin)
