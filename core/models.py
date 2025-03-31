from django.db import models, transaction
from datetime import date, timedelta
from decimal import Decimal
from django.core.exceptions import ValidationError
from authentication.models import User
from content.models import *



class Subscription(models.Model):
    PLAN_DURATIONS = {
        'monthly': 30,
        'quarterly': 90,
        'bi-yearly': 180,
        'yearly': 365
    }
    
    PLAN_PRICES = {
        'monthly': Decimal('9.99'),
        'quarterly': Decimal('26.97'),
        'bi-yearly': Decimal('53.94'),
        'yearly': Decimal('107.88')
    }

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions', db_index=True)
    plan_type = models.CharField(max_length=20, choices=[
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('bi-yearly', 'Bi-Yearly'),
        ('yearly', 'Yearly'),
    ])
    pricing = models.DecimalField(
        max_digits=6, 
        decimal_places=2,
        default=Decimal('0.00')
    )
    start_date = models.DateField(default=date.today)
    end_date = models.DateField()
    auto_renew = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    last_update_timestamp = models.DateTimeField(auto_now=True)
    creation_timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user'],
                condition=models.Q(active=True),
                name='single_active_subscription'
            )
        ]

        indexes = [
            models.Index(fields=['user', '-id',]),
            models.Index(fields=['active', 'auto_renew', 'end_date']),
        ]

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.pk:
                self.pricing = self.PLAN_PRICES[self.plan_type]
                self.end_date = self.start_date + timedelta(
                    days=self.PLAN_DURATIONS[self.plan_type]
                )
                Subscription.objects.select_for_update().filter(user=self.user, active=True).update(active=False)
                
                plan_price = self.PLAN_PRICES[self.plan_type]
                if self.user.wallet_balance < plan_price:
                    raise ValidationError(
                        f"Insufficient balance. Required: ${plan_price} for {self.get_plan_type_display()} Subscription, Available: ${self.user.wallet_balance}"
                    )
                
                self.user.wallet_balance -= plan_price
                self.user.save()
            self.full_clean()
        super().save(*args, **kwargs)
    
    def clean(self):
        with transaction.atomic():
            if self.pk:
                today = date.today()
                if not (self.start_date <= today <= self.end_date):
                    raise ValidationError("Cannot activate or update a subscription outside its validity period")
                Subscription.objects.select_for_update().filter(user=self.user, active=True).exclude(pk=self.pk).update(active=False)
        super().clean()

    @classmethod
    def get_price(cls, plan_type):
        return cls.PLAN_PRICES.get(plan_type, Decimal('0.00'))

    def __str__(self):
        return f"{self.user.email} - {self.plan_type} (${self.pricing})"
    
class UserInteraction(models.Model):
    INTERACTION_TYPES = [
        ('Viewed', 'Viewed'),
        ('Liked', 'Liked'),
        ('Skipped', 'Skipped'),
        ('Shared', 'Shared')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    content = models.ForeignKey(Content, on_delete=models.CASCADE, db_index=True)
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    last_update_timestamp = models.DateTimeField(auto_now=True)
    creation_timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', '-creation_timestamp']),
            models.Index(fields=['content', 'interaction_type']),
            models.Index(fields=['user', 'interaction_type']),
        ]