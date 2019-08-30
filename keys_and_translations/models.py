from django.db import models


class Key(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        try:
            return f'<Key {self.id}: {self.name}>'
        except:
            return super().__str__()


class Translation(models.Model):
    key = models.ForeignKey(Key, on_delete=models.CASCADE)
    locale = models.CharField(max_length=2)
    value = models.TextField(null=True, blank=True)

    def __str__(self):
        try:
            return f'<Translation {self.id}: {self.key_id} {self.locale} {self.value}>'
        except:
            return super().__str__()
