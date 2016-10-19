from __future__ import unicode_literals

from django.db import models


class Error(models.Model):
    S_WARNING = 'W'
    S_ERROR = 'E'

    SEVERITIES = (
        (S_WARNING, 'Warning'),
        (S_ERROR, 'Error')
    )

    date = models.DateTimeField()
    process_name = models.CharField(max_length=20)
    module_name = models.CharField(max_length=255)
    function_name = models.CharField(max_length=255)
    severity = models.CharField(max_length=1, choices=SEVERITIES)
    message = models.TextField()
    actionable_info = models.TextField(null=True)


class Feed(models.Model):
    url = models.CharField(max_length=255)
    date_launched = models.DateTimeField()
    date_finished = models.DateTimeField(null=True)
    update_date = models.DateTimeField()
    success = models.BooleanField()
    info = models.TextField(null=True)
