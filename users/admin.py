from django.contrib import admin

from .models import User, UserBusinessProfile, UserProfile, UserSubscription

admin.site.register(User)
admin.site.register(UserProfile)
admin.site.register(UserBusinessProfile)
admin.site.register(UserSubscription)
