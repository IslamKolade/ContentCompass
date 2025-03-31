from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import CustomUserManager
from decimal import Decimal
from django.db import transaction
from django.db.models import F



class User(AbstractUser):
    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    wallet_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    access_token = models.CharField(max_length=2000, null=True, blank=True)
    refresh_token = models.CharField(max_length=2000, null=True, blank=True)
    last_update_timestamp = models.DateTimeField(auto_now=True)
    creation_timestamp = models.DateTimeField(auto_now_add=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()
    username = None

    def credit_wallet(self, amount):
        try:
            amount = Decimal(amount)
        except:
            raise ValueError("Invalid amount")
        if amount <= Decimal('0.00'):
            raise ValueError("Amount must be a positive number")
        with transaction.atomic():
            self.__class__.objects.filter(id=self.id).update(wallet_balance=F('wallet_balance') + amount)

    def __str__(self):
        return self.email


