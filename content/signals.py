from django.db.models.signals import post_save, m2m_changed, pre_save
from django.dispatch import receiver
from django.core.cache import cache
from .models import Content
from core.models import UserInteraction



@receiver(post_save, sender=Content)
def handle_content_changes(sender, instance, created, **kwargs):
    if created:
        return
    
    if any(instance.tracker.has_changed(field) for field in instance.tracker.fields):
        invalidate_content_cache(instance)

@receiver(m2m_changed, sender=Content.tags.through)
def handle_tag_changes(sender, instance, action, **kwargs):
    if action in ['post_add', 'post_remove', 'post_clear']:
        if instance.pk:
            current_tags = set(instance.tags.names())
            original_tags = getattr(instance, '_original_tags', set())
            if current_tags != original_tags:
                print("Tags changed, invalidating cache")
                invalidate_content_cache(instance)
            else:
                print("Tags unchanged, skipping invalidation")

def invalidate_content_cache(content):
    user_ids = UserInteraction.objects.filter(
        content=content
    ).values_list('user_id', flat=True).distinct().iterator(chunk_size=1000)
    
    cache_keys = []
    
    for uid in user_ids:
        cache_keys.append(f"user_{uid}_content_recommendations")
        
        if len(cache_keys) >= 1000:
            cache.delete_many(cache_keys)
            cache_keys = []
    
    if cache_keys:
        cache.delete_many(cache_keys)