from django.contrib import admin

from .models import Review, ReviewedClient, Tag

admin.site.register(Tag)
admin.site.register(Review)
admin.site.register(ReviewedClient)
