# django & rest imports
from django.db import models

class Cities(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=17)
    slug = models.CharField(max_length=26, blank=True, null=True)
    province_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'cities'


class Provinces(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=19)
    slug = models.CharField(max_length=17)
    tel_prefix = models.CharField(max_length=3)

    class Meta:
        managed = False
        db_table = 'provinces'