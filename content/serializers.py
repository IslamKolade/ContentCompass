from rest_framework import serializers
from taggit.serializers import TagListSerializerField, TaggitSerializer
from .models import *
from authentication.serializers import *


class CategorySerializer(serializers.ModelSerializer):
    user = UserDetailSerializer(read_only=True)

    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ('slug', 'user')

class ContentSerializer(TaggitSerializer, serializers.ModelSerializer):
    user = UserDetailSerializer(read_only=True)
    category = CategorySerializer(read_only=True, many=False)
    tags = TagListSerializerField()

    class Meta:
        model = Content
        fields = '__all__'
        read_only_fields = ('slug', 'user', 'category', 'ai_relevance_score')

