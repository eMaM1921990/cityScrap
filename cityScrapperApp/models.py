# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import formatter

import django
import phonenumbers
from django.db import models

# Create your models here.
from django.db.models.base import Model

MANAGED = True


class ScrapModel(models.Model):
    name = models.TextField()
    source = models.CharField(max_length=100, null=False, default='FlipKey')
    created_date = models.DateField(default=django.utils.timezone.now)

    @property
    def count_has_numbers(self):
        return self.scrap_model.filter(phone__isnull=False).count()

    @property
    def count_all(self):
        return self.scrap_model.all().count()

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        managed = MANAGED
        db_table = 'scrap_model'


class ScrapDetails(models.Model):
    scrap = models.ForeignKey(ScrapModel, models.CASCADE, related_name='scrap_model', db_column='scrap_mode_id')
    name = models.CharField(max_length=150, null=True)
    f_name = models.CharField(max_length=150, null=True)
    l_name = models.CharField(max_length=150, null=True)
    phone = models.CharField(max_length=150, null=True)
    url = models.URLField()
    email = models.EmailField(null=True)

    def __unicode__(self):
        return self.name

    # def __str__(self):
    #     return self.name

    @property
    def format_phone_number(self):
        if self.phone:
            x = phonenumbers.parse(self.phone, None)
            return phonenumbers.format_number(x, phonenumbers.PhoneNumberFormat.E164)
        return '-'

    class Meta:
        managed = MANAGED
        db_table = 'scrap_details'


# class SalesForce(models.Model):
#     sales_force_id = models.CharField(max_length=250)
#     sales_force_phone = models.CharField(max_length=250, db_index=True)
#
#     def __unicode__(self):
#         return self.sales_force_phone
#
#     @property
#     def format_phone_number(self):
#         if self.sales_force_phone:
#             x = phonenumbers.parse(self.sales_force_phone, None)
#             return phonenumbers.format_number(x, phonenumbers.PhoneNumberFormat.E164)
#         return '-'
#
#     @property
#     def remove_number_format(self):
#         return str(self.sales_force_phone).replace("(", "").replace(")", "").replace("-", "").replace(" ", "")
#
#     class Meta:
#         managed = MANAGED
#         db_table = 'sales_force'


class CriagslistCities(models.Model):
    region = models.CharField(max_length=250)
    city = models.CharField(max_length=250)
    url = models.URLField()

    class Meta:
        managed = MANAGED
        db_table = 'criagslist_cities'
