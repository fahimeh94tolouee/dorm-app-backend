from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
import requests
from .serializers import RoomsSerializers, Room_UserSerializers, UserRelationsInRoomSerializers
from accounts.models import Account
from .models import Room, Room_User, UserRelationsInRoom, StateType, RelationStateType


@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def get_rooms(request):
    rooms = Room.objects.all()
    serializer = RoomsSerializers(rooms, many=True)
    return Response(data=serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated, ])
def request_room(request, room_id):
    room = Room.objects.filter(id=room_id).first()
    if room is not None:
        user = request.user
        account = Account.objects.filter(user=user).first()
        roomWithUsers = Room_User.objects.filter(room_id=room_id)
        userRoom = Room_User.objects.filter(user=account).first()
        if userRoom is None:
            roomMembersNum = len(roomWithUsers)
            if roomMembersNum == 0:
                serializer = Room_UserSerializers(
                    data={"user": account.id, "room": room.id, "user_state": StateType.OK})
                if serializer.is_valid():
                    serializer.save()
                    data = {"message": "به اتاق اضافه شدید."}
                    return Response(data)
                else:
                    print(serializer.errors)
                    data = {"message": "دیتا ناصحیح است."}
                    return Response(data)
            else:
                if roomMembersNum < room.capacity:
                    print(roomMembersNum, "EE")
                    serializer = Room_UserSerializers(
                        data={"user": account.id, "room": room.id, "user_state": StateType.PENDING})
                    serializer.is_valid()
                    print(serializer.errors, " room-user")
                    serializer.save()
                    for row in roomWithUsers:
                        serializer = UserRelationsInRoomSerializers(
                            data={
                                "user1": account.id,
                                "user2": row.user_id,
                                "user1_to_user2_state": RelationStateType.OK
                            }
                        )
                        serializer.is_valid()
                        print(serializer.errors, " user-relations- inRoom-> requester")
                        serializer.save()
                        if row.user_state == StateType.OK:
                            serializer = UserRelationsInRoomSerializers(
                                data={
                                    "user1": row.user_id,
                                    "user2": account.id,
                                    "user1_to_user2_state": RelationStateType.PENDING
                                }
                            )
                            serializer.is_valid()
                            print(serializer.errors, " user-relations- requester->inRoom")
                            serializer.save()

                        elif row.user_state == StateType.PENDING:
                            serializer = UserRelationsInRoomSerializers(
                                data={
                                    "user1": row.user_id,
                                    "user2": account.id,
                                    "user1_to_user2_state": RelationStateType.UNKNOWN
                                }
                            )
                            serializer.is_valid()
                            print(serializer.errors, " user-relations- requester->inRoom")
                            serializer.save()
                        # print(row.user_id)
                    data = {"message": "درخواست شما ارسال شد."}
                    return Response(data)
                else:
                    data = {"message": "ظرفیت اتاق تکمیل است."}
                    return Response(data, status=status.HTTP_400_BAD_REQUEST)
        else:
            state = userRoom.user_state
            user_room = userRoom.room
            text = ""
            print(user_room, state, "PP")
            if state == StateType.OK:
                text = " به عنوان عضو "
            elif state == StateType.PENDING:
                text = " به عنوان منتظر "
            data = {"message": "شما در اتاق " + str(user_room) + text + "ثبت شده‌اید."}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

    else:
        data = {"message": "اتاق مورد نظر پیدا نشد."}
        return Response(data, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated, ])
def answer_user(request, user_id):
    answer = request.data['answer']  # true or false
    data = {"data": "", "message": ""}
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def get_pended_user(request):
    data = {"message": ""}
    user = request.user
    account = Account.objects.filter(user=user).first()
    pendedUsers = UserRelationsInRoom.objects.filter(user1=account, user1_to_user2_state=RelationStateType.PENDING)
    print(list(pendedUsers))
    serializer = UserRelationsInRoomSerializers(list(pendedUsers), many=True)
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, ])
def delete_request(request):
    data = {"data": "", "message": ""}
    return Response(data)
