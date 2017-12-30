# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class TravelmobappConfig(AppConfig):
    name = 'CityScrappers'

    def ready(self):
        import Signals
