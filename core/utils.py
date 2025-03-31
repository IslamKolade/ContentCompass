from django.conf import settings
from django.db.models import F
from django.contrib.auth.hashers import check_password
from django.utils.translation import gettext as _
from rest_framework.response import Response
from rest_framework import status
from authentication.models import User
from rest_framework_simplejwt.tokens import AccessToken
import jwt
import re
from decimal import Decimal
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.core.mail import BadHeaderError, EmailMessage
from django.template.loader import render_to_string 
from decouple import config



def success(data=None, message='Success', otp=False):
    response_data = {'error': False, 'data': data, 'message': message}
    
    if otp:
        response_data['otp'] = True
    
    return Response(status=status.HTTP_200_OK, data=response_data)

def error(data=None, message='Error'):
    response_data = {'error': True, 'data': data, 'message': message}
    return Response(status=status.HTTP_400_BAD_REQUEST, data=response_data)

def camel_case_to_spaces(name):
    return re.sub(r'(?<!^)(?=[A-Z])', ' ', name)

def get_object_or_404_json(klass, *args, **kwargs):
    try:
        return klass.objects.get(*args, **kwargs)
    except ObjectDoesNotExist:
        class_name = camel_case_to_spaces(klass.__name__)
        raise ValidationError(f'{class_name} not found')

def get_user_by_email(email):
    return get_object_or_404_json(User, email=email)

def check_required_fields(data, required_fields):
    missing_or_empty_fields = [
        field for field in required_fields 
        if field not in data or (isinstance(data[field], str) and not data[field].strip())
    ]
    if missing_or_empty_fields:
        raise ValidationError(f"Missing or empty required fields: {', '.join(missing_or_empty_fields)}")

def parse_bool(value, field_name=None):
    if value is None:
        return None
    
    if isinstance(value, bool):
        return value
    
    if isinstance(value, str):
        value = value.strip().lower()
        if value == 'true':
            return True
        if value == 'false':
            return False
    
    field_info = f" for field '{field_name}'" if field_name else ""
    raise ValueError(
        f"Invalid boolean value{field_info}. Only 'true' or 'false' allowed."
    )


def validate_name_format(name):
    if not name:
        return name
    
    name = name.strip()

    if len(name) < 2 or len(name) > 50:
        raise ValidationError("Name must be between 2-50 characters")

    if not re.match(r"^[a-zA-Z'-]+$", name):
        raise ValidationError("Name can only contain letters, hyphens (-), and apostrophes (')")

    if name[0] in ("-", "'") or name[-1] in ("-", "'"):
        raise ValidationError("Name cannot start/end with hyphen or apostrophe")
    
    if re.search(r"[-']{2,}", name):
        raise ValidationError("Name cannot have consecutive hyphens/apostrophes")

    return name