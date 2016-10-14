from django.contrib import admin
from .models import Error

# Register your models here.


class ErrorAdmin(admin.ModelAdmin):
    # define which columns displayed in changelist
    list_display = ('date', 'severity', 'process_name', 'module_name', 'function_name')
    # add filtering by date
    list_filter = ('process_name',)

admin.site.register(Error, ErrorAdmin)
