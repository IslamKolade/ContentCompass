from celery import shared_task
from datetime import date, timedelta
from django.db import transaction
from .models import Subscription
from authentication.models import User

@shared_task
def handle_subscription_lifecycle():
    today = date.today()
    
    with transaction.atomic():
        expired_subs = Subscription.objects.filter(
            active=True,
            end_date__lt=today
        ).select_related('user')
        
        for sub in expired_subs:
            user = User.objects.select_for_update().get(pk=sub.user.id)
            sub.active = False
            sub.save()
            
            if sub.auto_renew:
                process_renewal(user, sub.plan_type, sub.end_date)

        renewing_subs = Subscription.objects.filter(
            active=True,
            auto_renew=True,
            end_date=today
        ).select_related('user')
        
        for sub in renewing_subs:
            user = User.objects.select_for_update().get(pk=sub.user.id)
            process_renewal(user, sub.plan_type, sub.end_date)
            sub.active = False
            sub.save()

def process_renewal(user, plan_type, previous_end_date):
    price = Subscription.get_price(plan_type)
    
    if user.wallet_balance >= price:
        user.wallet_balance -= price
        user.save()
        
        new_start = previous_end_date + timedelta(days=1)
        Subscription.objects.create(
            user=user,
            plan_type=plan_type,
            start_date=new_start,
            auto_renew=True
        )
    else:
        #Want to add an email that informs the user of the failed auto-renewal due to insufficient balance
        pass