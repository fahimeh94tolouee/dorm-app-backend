from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
import requests
from .serializers import LogMessageSerializers
from .models import LogMessage
from accounts.models import Account


@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def get_all_logs(request):
    user = request.user
    account = Account.objects.filter(user=user).first()
    logs = LogMessage.objects.filter(user=account)
    print(logs, "LOGS")
    serializer = LogMessageSerializers(logs, many=True)
    return Response(data=serializer.data, status=status.HTTP_200_OK)
