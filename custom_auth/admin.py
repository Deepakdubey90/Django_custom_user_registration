from django.contrib import admin
from .models import MyUser


class AuthorAdmin(admin.ModelAdmin):
    pass

admin.site.register(MyUser, AuthorAdmin)
