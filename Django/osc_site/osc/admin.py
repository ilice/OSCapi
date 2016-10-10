from django.contrib import admin
from .models import BatchProcess, Error

# Register your models here.


class BatchProcessAdmin(admin.ModelAdmin):
    # define which columns displayed in changelist
    list_display = ('name', 'status', 'date_launched', 'date_finished')
    # add filtering by date
    list_filter = ('name',)

admin.site.register(BatchProcess, BatchProcessAdmin)


class ErrorAdmin(admin.ModelAdmin):
    # define which columns displayed in changelist
    list_display = ('date', 'severity', 'process_name', 'module_name', 'function_name')
    # add filtering by date
    list_filter = ('process_name',)

admin.site.register(Error, ErrorAdmin)
