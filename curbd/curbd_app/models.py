from django.contrib.auth.models import User
from django.db import models


class Item(models.Model):
    name = models.CharField(max_length=200)
    price = models.FloatField(default=0)
    create_date = models.DateTimeField('date create')
    location = models.CharField(max_length=200)
    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name
