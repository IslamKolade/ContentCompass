from celery import shared_task
from .utils import *
from ContentCompass.celery import app



@app.task(bind=True, autoretry_for=(Exception,), retry_backoff=60)
def async_update_content_recommendations(self, user_id):
    from django.contrib.auth import get_user_model
    user = get_user_model().objects.get(id=user_id)
    
    recommendations = calculate_content_recommendations(user)
    
    return recommendations