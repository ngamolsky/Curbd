from django.db import models


class Item(models.Model):
    name = models.CharField(max_length=200)
    price = models.FloatField(default=0)
    create_date = models.DateTimeField('date created')
    location = models.CharField(max_length=200)

    def __str__(self):
        return self.name
