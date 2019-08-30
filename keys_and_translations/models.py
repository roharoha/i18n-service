from django.db import models


class Key(models.Model):
    name = models.CharField(max_length=255)


class Translation(models.Model):
    key = models.ForeignKey(Key, on_delete=models.CASCADE)
    locale = models.CharField(max_length=2)
    value = models.TextField(null=True, blank=True)
