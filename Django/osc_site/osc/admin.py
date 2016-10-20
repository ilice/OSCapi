from django.contrib import admin
from .models import Error, Feed

# Register your models here.


class ErrorAdmin(admin.ModelAdmin):
    # define which columns displayed in changelist
    list_display = ('date', 'severity', 'process_name', 'module_name', 'function_name')
    # add filtering by date
    list_filter = ('process_name',)

admin.site.register(Error, ErrorAdmin)


class FeedAdmin(admin.ModelAdmin):
    # define which columns displayed in changelist
    list_display = ('url', 'date_launched', 'update_date', 'success', )
    # add filtering by date
    list_filter = ('success',)

admin.site.register(Feed, FeedAdmin)
