from django.db import models


class Book(models.Model):
    name = models.CharField(max_length=100)
    price = models.PositiveSmallIntegerField(blank=True, null=True)

    def __str__(self):
        return self.name
