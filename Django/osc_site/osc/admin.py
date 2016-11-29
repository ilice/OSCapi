from django.contrib import admin
from .models import Error, Feed, UserProfile, UserParcel

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


class UserProfileAdmin(admin.ModelAdmin):
    # define which columns displayed in changelist
    list_display = ('user', )

admin.site.register(UserProfile, UserProfileAdmin)


class UserParcelAdmin(admin.ModelAdmin):
    # define which columns displayed in changelist
    list_display = ('user', 'cadastral_code',)

admin.site.register(UserParcel, UserParcelAdmin)
