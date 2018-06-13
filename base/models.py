# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=50)

class Product(models.Model):
    name = models.CharField(max_length=50)
    category = models.ForeignKey(Category, null=True, blank=True)
    description = models.TextField()
    creator = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    base_fare = models.FloatField(default=0, blank=True, null=True)
    margin = models.FloatField(default=0, blank=True, null=True)
    total_fare = models.FloatField()
