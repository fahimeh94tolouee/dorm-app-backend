# from django.shortcuts import render
from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError
from django.db import models
from rest_framework import status
from rest_framework.exceptions import APIException
from django.utils.translation import gettext_lazy as _
from django.http import Http404


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    # check that a ValidationError exception is raised
    if isinstance(exc, ValidationError):
        # here prepare the 'custom_error_response' and
        # set the custom response data on response object
        if response.data.get("username", None):
            response.data = response.data["username"][0]
        elif response.data.get("email", None):
            response.data = response.data["email"][0]
        elif response.data.get("password", None):
            response.data = response.data["password"][0]

    return response


class ServiceUnavailable(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'سرور در حال حاضر در دسترس نیست، لطفا بعدا تلاش کنید.'


class ParseError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('ورودی صحبح نمی‌باشد.')
    default_code = 'parse_error'


class AuthenticationFailed(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _('')
    default_code = 'authentication_failed'


class NotAuthenticated(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _('توکن یافت نشد.')
    default_code = 'not_authenticated'


class PermissionDenied(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = _('You do not have permission to perform this action.')
    default_code = 'permission_denied'


class NotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _('پیدا نشد')
    default_code = 'not_found'