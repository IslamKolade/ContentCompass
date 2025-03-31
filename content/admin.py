from django.contrib import admin
from django.contrib import admin
from .models import *
from django.utils.translation import gettext_lazy as _



@admin.register(Category)
class Category_Admin(admin.ModelAdmin):
    search_fields = ('user', 'name', 'description')
    readonly_fields = ('user', 'slug', 'last_update_timestamp', 'creation_timestamp')
    list_display = ('id', 'user', 'name', 'last_update_timestamp', 'creation_timestamp')
    list_display_links = ('id', 'user', 'name',)
        
    def get_changelist_instance(self, request):
        changelist = super().get_changelist_instance(request)
        changelist.title = _("Categories")
        return changelist
        
    def save_model(self, request, obj, form, change):
        if not obj.user:
            obj.user = request.user
        obj.save()

@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'category', 'ai_relevance_score', 'last_update_timestamp', 'creation_timestamp')
    list_display_links = ('id', 'user', 'title', 'category',)
    list_filter = ('category', 'tags',)
    readonly_fields = ('user', 'slug', 'ai_relevance_score', 'last_update_timestamp', 'creation_timestamp')
    search_fields = ('user', 'title', 'description')

    def save_model(self, request, obj, form, change):
        if not obj.user:
            obj.user = request.user
        obj.save()