from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import UserInteraction
from content.tasks import async_update_content_recommendations

@receiver([post_save, post_delete], sender=UserInteraction)
def trigger_async_update(sender, instance, **kwargs):
    user_id = instance.user_id
    
    if user_id:
        async_update_content_recommendations.delay(user_id)