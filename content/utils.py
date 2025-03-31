from core.models import UserInteraction
from django.db.models import Count, Q, Case, When, IntegerField
from django.db.models.functions import Coalesce
from .models import *
from .serializers import *
from django.core.cache import cache



def calculate_content_recommendations(user):
    interacted_content_ids = UserInteraction.objects.filter(
        user=user
    ).values_list('content_id', flat=True)
    
    interactions = UserInteraction.objects.filter(
        user=user,
        interaction_type__in=['Liked', 'Viewed', 'Shared']
    ).select_related('content__category')
    
    preferred_tags = set()
    preferred_categories = set()
    
    for interaction in interactions:
        preferred_tags.update(tag.name for tag in interaction.content.tags.all())
        
        if interaction.content.category:
            preferred_categories.add(interaction.content.category.name)
    
    use_ai_fallback = not (preferred_tags or preferred_categories)
    
    base_query = Content.objects.exclude(id__in=interacted_content_ids)
    
    if use_ai_fallback:
        recommendations = base_query.order_by('-ai_relevance_score')[:5]
    else:
        recommendations = base_query.annotate(
            tag_match_score=Coalesce(
                Count('tags', filter=Q(tags__name__in=preferred_tags)),
                0
            ),
            category_match_score=Case(
                When(
                    category__isnull=False,
                    category__name__in=preferred_categories,
                    then=1
                ),
                default=0,
                output_field=IntegerField()
            ),
            combined_score=(
                F('ai_relevance_score') * 0.4 +
                F('tag_match_score') * 0.4 +
                F('category_match_score') * 0.2
            )
        ).order_by('-combined_score')[:5]
    
    if not recommendations.exists():
        recommendations = Content.objects.order_by('-ai_relevance_score')[:5]

    cache_key = f"user_{user.id}_content_recommendations"

    serializer = ContentSerializer(recommendations, many=True)
    data = serializer.data
    cache.set(cache_key, data, timeout=60)
    return data