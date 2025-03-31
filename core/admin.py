from django.contrib import admin
from .models import *
from django.utils.translation import gettext_lazy as _
from admin_interface.models import Theme



admin.site.site_header = 'Content Compass Admin Dashboard'
admin.site.site_title = 'Content Compass Admin Dashboard'
admin.site.index_title = 'Welcome to the Content Compass Admin Dashboard'

#admin.site.unregister(Theme)

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'plan_type', 'start_date', 'end_date', 'auto_renew', 'active', 'last_update_timestamp', 'creation_timestamp')
    list_display_links = ('id', 'user', 'plan_type', 'start_date', 'end_date',)
    list_filter = ('plan_type', 'auto_renew', 'active',)
    readonly_fields = ('end_date', 'pricing', 'last_update_timestamp', 'creation_timestamp')
    search_fields = ('user',)

@admin.register(UserInteraction)
class UserInteractionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'content', 'interaction_type', 'last_update_timestamp', 'creation_timestamp')
    list_display_links = ('id', 'user', 'content', 'interaction_type',)
    list_filter = ('interaction_type',)
    readonly_fields = ('last_update_timestamp', 'creation_timestamp')
    search_fields = ('user',)

