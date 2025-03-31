from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.hashers import make_password
from .models import *
from django.contrib.auth import authenticate
from .serializers import *
from core.utils import *
from core.models import *
from .utils import *
from rest_framework_simplejwt.tokens import RefreshToken
import requests
from django.utils import timezone
from disposable_email_checker.validators import validate_disposable_email
from django_ratelimit.decorators import ratelimit



@api_view(['POST'])
@ratelimit(key='user_or_ip', rate='2/10m', block=True, method='POST')
@permission_classes([permissions.AllowAny])
def signup(request):
    try:
        data = request.data
        email = data.get('email')
        first_name = validate_name_format(data.get('first_name'))
        last_name = validate_name_format(data.get('last_name'))
        password = validate_user_password(data.get('password'))
        confirm_password = data.get('confirm_password')

        required_fields = ["email", "password", "confirm_password"]

        check_required_fields(request.data, required_fields)

        if password != confirm_password:
            return error(message="Passwords do not match")

        try:
            validate_disposable_email(email)
        except:
            return error(message="Disposable email addresses are not allowed")

        if User.objects.filter(email=email).exists():
            return error(message="Email is already in use")

        user = User.objects.create(
            email=email,
            first_name=first_name.upper(),
            last_name=last_name.upper(),
            password=make_password(password)
        )

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        user.access_token = access_token
        user.refresh_token = refresh_token

        user.last_login = timezone.now()
        user.save()
        user_serializer = UserSerializer(user, many=False)
        return success(message="User registered successfully", data={"user" : user_serializer.data})
    except ValidationError as e:
        return error(message=f"{e.messages[0]}")
    except Exception as e:
        return error(message=str(e))

@api_view(['POST'])
@ratelimit(key='user_or_ip', rate='5/15m', block=True, method='POST')
@permission_classes([permissions.AllowAny])
def login(request):
    try:
        data = request.data
        email = data.get('email')
        password = data.get('password')

        required_fields = ["email", "password"]

        check_required_fields(request.data, required_fields)

        user = authenticate(email=email, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            
            user.access_token = access_token
            user.refresh_token = refresh_token

            user.last_login = timezone.now()
            user.save()
            user_serializer = UserSerializer(user,many=False)
            return success(message="Login successful", data={"user" : user_serializer.data})
        else:
            return error(message='Invalid login details') 
    except ValidationError as e:
        return error(message=f"{e.messages[0]}")
    except Exception as e:
        return error(message=str(e))

@api_view(['POST'])
@ratelimit(key='user_or_ip', rate='5/15m', block=True, method='POST')
@permission_classes([permissions.AllowAny])
def refresh_access_token(request):
    try:
        refresh_token = request.data.get('refresh_token')

        required_fields = ["refresh_token"]
        check_required_fields(request.data, required_fields)

        response = requests.post(
            request.build_absolute_uri('/auth/api/token/refresh/'),
            data={'refresh': refresh_token}
        )
        response_data = response.json()
        if response.status_code == 200:
            new_access_token = response_data.get('access')

            if new_access_token:
                decoded_payload = RefreshToken(refresh_token).payload
                user_id = decoded_payload.get('user_id')

                user = User.objects.get(id=user_id)
                user.access_token = new_access_token
                user.save()

            return success(data=response_data)

        return error(data=response_data)
    except ValidationError as e:
        return error(message=f"{e.messages[0]}")
    except Exception as e:
        return error(message=str(e))