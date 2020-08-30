from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from project_final.settings import BASE_ROUTE, CLIENT_ID, CLIENT_SECRET
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
import requests
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from .serializers import AccountSerializer, UserSerializer
from .models import Account


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Registers user to the server. Input should be in the format:
    {"username": "username", "password": "1234abcd"}
    """
    # Put the data from the request into the serializer

    serializer = UserSerializer(data=request.data)
    # Validate the data
    if serializer.is_valid():
        # If it is valid, save the data (creates a user).
        serializer.save()
        # Then we get a token for the created user.
        # This could be done differently
        r = requests.post(BASE_ROUTE + '/o/token/',
                          data={
                              'grant_type': 'password',
                              'username': request.data['username'],
                              'password': request.data['password'],
                              'client_id': CLIENT_ID,
                              'client_secret': CLIENT_SECRET,
                          },
                          )

        data = {"data": r.json(), "message": "با موفقیت ثبت نام شدید."}
        return Response(data=data, status=status.HTTP_200_OK)
    print(serializer.errors)
    return Response(serializer.errors)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Gets tokens with username and password. Input should be in the format:
    {"username": "username", "password": "1234abcd"}
    """
    r = requests.post(
        BASE_ROUTE + '/o/token/',
        data={
            'grant_type': 'password',
            'username': request.data['username'],
            'password': request.data['password'],
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
        },
    )
    message = ""
    # r.headers['Access-Control-Allow-Origin'] = '*'
    if r.status_code == status.HTTP_400_BAD_REQUEST:
        message = "نام کاربری و یا رمز عبور اشتباه است."
    if r.status_code == status.HTTP_401_UNAUTHORIZED:
        message = "کاربری با این مشخصات پیدا نشد."
    elif r.status_code == status.HTTP_200_OK:
        message = "با موفقیت وارد شدید."
    data = {"data": r.json(), "message": message}
    return Response(data=data, status=r.status_code)


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    """
    Registers user to the server. Input should be in the format:
    {"refresh_token": "<token>"}
    """
    r = requests.post(
        BASE_ROUTE + '/o/token/',
        data={
            'grant_type': 'refresh_token',
            'refresh_token': request.data['refresh_token'],
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
        },
    )
    return Response(r.json())


@api_view(['POST'])
@permission_classes([AllowAny])
def revoke_token(request):
    """
    Method to revoke tokens.
    {"token": "<token>"}
    """
    r = requests.post(
        BASE_ROUTE + '/o/revoke_token/',
        data={
            'token': request.data['token'],
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
        },
    )
    # If it goes well return success message (would be empty otherwise)
    if r.status_code == requests.codes.ok:
        return Response({'message': 'token revoked'}, r.status_code)
    # Return the error if it goes badly
    return Response(r.json(), r.status_code)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_account(request):
    # if isinstance(request.user, User):
    account = Account.objects.filter(user=request.user).first()
    if account is None:
        data = {"message": "کاربر مورد نظر یافت نشد."}
        return Response(data, status.HTTP_404_NOT_FOUND)
    else:
        serializer = AccountSerializer(account)
        return Response(serializer.data)


@api_view(['PUT'])
@permission_classes((IsAuthenticated,))
def update_account(request):
    if isinstance(request.user, User):
        account = Account.objects.filter(user=request.user).first()
        # print(serializer.is_valid(), request.data)
        # print(request.data, "RRR")
        # data = JSONParser().parse(request.data)
        serializer = AccountSerializer(account, data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = {"data": serializer.data, "message": "اطلاعات حساب شما باموفیت به روز رسانی شد."}
            return Response(data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

