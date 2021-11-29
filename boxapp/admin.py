from django.contrib import admin

# Register your models here.

from .models import Profile,Store,Box

admin.site.register(Profile)
admin.site.register(Store)
admin.site.register(Box)