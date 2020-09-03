from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import Account
from accounts.serializers import AccountSerializer


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def init(request):
    account = Account.objects.filter(user=request.user).first()
    data = {"data": {}, "message": ''}
    responseStatus = status.HTTP_200_OK
    if account is None:
        data["message"] = "کاربر مورد نظر یافت نشد."
        responseStatus = status.HTTP_404_NOT_FOUND
    else:
        serializer = AccountSerializer(account)
        data["data"]["user"] = serializer.data
    return Response(data, responseStatus)
