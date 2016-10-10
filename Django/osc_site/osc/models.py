from __future__ import unicode_literals

from django.db import models


# Create your models here.
from docutils.parsers.rst.directives import choice


class BatchProcess(models.Model):
    P_INFORIEGO_DAILY = 'IR_D'
    P_INFORIEGO_HOURLY = 'IR_H'
    P_SIGPAC_PLOTS = 'SP_P'

    PROCESS_NAMES = (
        (P_INFORIEGO_DAILY, 'Inforiego Daily'),
        (P_INFORIEGO_HOURLY, 'Inforiego Hourly'),
        (P_SIGPAC_PLOTS, 'SIGPAC Plots')
    )

    S_PROCESS = 'P'
    S_FAILED = 'F'
    S_SUCCESS = 'S'
    S_CANCELLED = 'C'

    PROCESS_STATUS = (
        (S_PROCESS, 'In Process'),
        (S_FAILED, 'Failed'),
        (S_SUCCESS, 'Success'),
        (S_CANCELLED, 'Cancelled')
    )

    name = models.CharField(max_length=4, choices=PROCESS_NAMES)
    status = models.CharField(max_length=1, choices=PROCESS_STATUS)
    date_launched = models.DateTimeField()
    date_finished = models.DateTimeField(null=True)


class Error(models.Model):
    PROCESS_NAMES = BatchProcess.PROCESS_NAMES

    S_WARNING = 'W'
    S_ERROR = 'E'

    SEVERITIES = (
        (S_WARNING, 'Warning'),
        (S_ERROR, 'Error')
    )

    date = models.DateTimeField()
    process_name = models.CharField(max_length=4, choices=PROCESS_NAMES)
    module_name = models.CharField(max_length=255)
    function_name = models.CharField(max_length=255)
    severity = models.CharField(max_length=1, choices=SEVERITIES)
    message = models.TextField()
    actionable_info = models.TextField()
