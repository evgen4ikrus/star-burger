from django.db import models


class Place(models.Model):
    address = models.CharField('адркс', max_length=200, unique=True)
    latitude = models.FloatField('широта', blank=True, null=True)
    longitude = models.FloatField('долгота', blank=True, null=True)
    update_at = models.DateTimeField('дата и время запроса к геокодеру', auto_now=True, db_index=True)

    class Meta:
        verbose_name = 'место на карте'
        verbose_name_plural = 'места на карте'

    def __str__(self):
        return self.address
