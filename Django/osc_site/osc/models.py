from __future__ import unicode_literals

from django.db import models


# Create your models here.
class BatchProcess(models.Model):
    PROCESS_NAMES = (
        ('IR_D', 'Inforiego Daily'),
        ('IR_H', 'Inforiego Hourly')
    )

    PROCESS_STATUS = (
        ('P', 'In Process'),
        ('F', 'Failed'),
        ('S', 'Success')
    )

    name = models.CharField(max_length=4, choices=PROCESS_NAMES)
    status = models.CharField(max_length=1, choices=PROCESS_STATUS)
    date_launched = models.DateTimeField()
    date_finished = models.DateTimeField(null=True)
