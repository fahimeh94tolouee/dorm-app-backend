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
    if account is None:
        data = {"message": "کاربر مورد نظر یافت نشد."}
        return Response(data, status.HTTP_404_NOT_FOUND)
    else:
        serializer = AccountSerializer(account)
        return Response(serializer.data)