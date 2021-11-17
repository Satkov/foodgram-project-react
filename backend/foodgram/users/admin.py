from django.contrib import admin

from .models import Follow, User


class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name')
    search_fields = ['username', 'email']


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user',)
    filter_horizontal = ('author',)


admin.site.register(User, UserAdmin)
admin.site.register(Follow, FollowAdmin)
