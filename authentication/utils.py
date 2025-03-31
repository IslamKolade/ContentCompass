from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.contrib.auth.password_validation import validate_password
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
   
   

def get_client_ip(request):
    return request.META.get('HTTP_X_REAL_IP') or request.META.get('REMOTE_ADDR')
   
def validate_password_strength(value):
    if not any(char.isupper() for char in value):
        raise ValidationError(_("The password must contain at least one uppercase letter"), code='password_no_uppercase')
    if not any(char.islower() for char in value):
        raise ValidationError(_("The password must contain at least one lowercase letter"), code='password_no_lowercase')
    if not any(char.isdigit() for char in value):
        raise ValidationError(_("The password must contain at least one numeric digit (0–9)."), code='password_no_numeric')
    if not re.search(r'[^\w\s]', value):
        raise ValidationError(_("The password must contain at least one special character"), code='password_no_special')

def validate_user_password(password):
    MinLengthValidator(8)(password)
    MaxLengthValidator(128)(password)
    validate_password(password)
    validate_password_strength(password)
    return password