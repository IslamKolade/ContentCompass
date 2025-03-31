from authentication.models import *
from rest_framework.decorators import api_view
from authentication.serializers import *
from core.utils import *
from .models import *
from .serializers import *
from django.shortcuts import redirect




@api_view(['GET'])
def user_data(request):
    try:
        user_serializer = UserSerializer(request.user, many=False)
        data = user_serializer.data
        return success(data={"user": data})
    except ValidationError as e:
        return error(message=f"{e.messages[0]}")
    except Exception as e:
        return error(message=str(e))

@api_view(['POST'])
def fund_wallet(request):
    try:
        user = request.user
        data = request.data
        if request.method == 'POST':
            amount = data.get('amount')
            
            required_fields = ["amount",]

            check_required_fields(data, required_fields)

            user.credit_wallet(amount)

            user.refresh_from_db()
            
            return success(data={"amount_funded": str(Decimal(amount)), "new_balance": str(user.wallet_balance)},message="Wallet funded successfully")
    except ValidationError as e:
        return error(message=f"{e.messages[0]}")
    except Exception as e:
        return error(message=str(e))

@api_view(['GET', 'POST'])
def subscriptions(request):
    try:
        user = request.user
        data = request.data
        if request.method == 'GET':
            subscriptions = Subscription.objects.filter(user=user).order_by('-id')

            return success(data={
                "subscriptions": SubscriptionSerializer(subscriptions, many=True).data,
                "available_plans": {
                    plan: {
                        "price": str(Subscription.PLAN_PRICES[plan]),
                        "duration_days": Subscription.PLAN_DURATIONS[plan]
                    }
                    for plan in Subscription.PLAN_PRICES
                }
            })
        elif request.method == 'POST':
            plan_type = data.get('plan_type')
            auto_renew = parse_bool(data.get('auto_renew'), 'auto_renew')
            
            required_fields = ["plan_type",]

            check_required_fields(data, required_fields)
            
            if plan_type not in Subscription.PLAN_PRICES:
                return error(message=f"Invalid plan type - {plan_type}")
            
            subscription = Subscription.objects.create(
                user=request.user,
                plan_type=plan_type,
                auto_renew= auto_renew
            )
            serializer = SubscriptionSerializer(subscription)
            return success(data=serializer.data, message="Subscription created")
    except ValidationError as e:
        return error(message=f"{e.messages[0]}")
    except Exception as e:
        return error(message=str(e))

@api_view(['GET', 'PATCH'])
def subscription(request, id):
    try:
        user = request.user
        data = request.data
        subscription = get_object_or_404_json(Subscription, id=id, user=user)
        
        if request.method == 'GET':
            serializer = SubscriptionSerializer(subscription)
            return success(data=serializer.data)
        elif request.method == 'PATCH':
            allowed_fields = ['auto_renew', 'active']

            if not any(field in data for field in allowed_fields):
                return error(message=f"Must provide at least one updatable field: {', '.join(allowed_fields)}")

            updates = {}
            
            for field in allowed_fields:
                if field in data:
                    updates[field] = parse_bool(
                        data[field], 
                        field_name=field
                    )
            
            for key, value in updates.items():
                setattr(subscription, key, value)

            subscription.save()
            serializer = SubscriptionSerializer(subscription)
            return success(data=serializer.data, message="Subscription updated")
    except ValidationError as e:
        return error(message=f"{e.messages[0]}")
    except Exception as e:
        return error(message=str(e))

def redirect_logo(request):
    return redirect('http://localhost:8000/static/logo/logo.svg', permanent=True)

def redirect_favicon(request):
    return redirect('http://localhost:8000/static/favicon/logo.svg', permanent=True)
