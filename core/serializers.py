from rest_framework import serializers
from .models import *
from authentication.serializers import *


class SubscriptionSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer(read_only=True)

    class Meta:
        model = Subscription
        fields = '__all__'
        ord
