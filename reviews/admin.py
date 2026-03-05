from django.contrib import admin
from .models import Tag, Review, ReviewedClient


admin.site.register(Tag)
admin.site.register(Review)
admin.site.register(ReviewedClient)
