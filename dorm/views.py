from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
import requests
from .serializers import RoomsSerializers, Room_UserSerializers, UserRelationsInRoomSerializers
from accounts.models import Account
from accounts.serializers import AccountSerializer
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
def answer_user(request):
    message = ""
    answer = request.data['answer']  # true or false
    pended_account_id = request.data['pended_account_id']
    responder_user_id = request.user
    responder_account = Account.objects.filter(user=responder_user_id).first()
    pended_account = Account.objects.filter(id=pended_account_id).first()
    rowInPendedAccountAndRespondedAccountInRelationTable = UserRelationsInRoom.objects.filter(
        user1=responder_account.id,
        user2=pended_account_id,
        user1_to_user2_state=RelationStateType.PENDING
    ).first()

    if (pended_account is not None) and (rowInPendedAccountAndRespondedAccountInRelationTable is not None):
        if answer:
            data = {"user1": responder_account.id, "user2": pended_account_id,
                    "user1_to_user2_state": RelationStateType.OK}
            serializer = UserRelationsInRoomSerializers(rowInPendedAccountAndRespondedAccountInRelationTable, data=data)
            serializer.is_valid()
            serializer.save()
            message = checkAddToRoom(pended_account_id, responder_account.id)
        else:
            pass
            # TODO delete relations Row and user_room Rows
            message = "رد فرد مورد نظر با موفقیت انجام شد."
    else:
        message = "کاربر مورد نظر شما یافت نشد!"
    room_user_row = Room_User.objects.filter(user=pended_account_id).first()
    all_corresponding_room_user_rows = Room_User.objects.filter(room=room_user_row.room.id)
    all_user_with_state = Account.objects.filter(id__in=all_corresponding_room_user_rows.values('user_id'))
    print(all_user_with_state, "TTTT")
    membersListSerializer = Room_UserSerializers(list(all_corresponding_room_user_rows), many=True)
    data = {"data": membersListSerializer.data, "message": message}
    return Response(data)


def checkAddToRoom(pended_id, responder_id):
    message = ""
    room_user_row = Room_User.objects.filter(user=pended_id).first()
    room_user_row_confirm = Room_User.objects.filter(user=responder_id).first()
    if (room_user_row_confirm is not None) and (room_user_row.room == room_user_row_confirm.room):
        room = room_user_row.room
        real_room_member_rows = Room_User.objects.filter(room=room,
                                                         user_state=StateType.OK)  # All confirmed room members
        # print(real_room_member_rows, "RR")
        confirm = True
        for row in real_room_member_rows:
            real_member_id = row.user_id
            row_for_real_member_ok_with_pended_member = UserRelationsInRoom.objects.filter(
                user1=real_member_id, user2=pended_id, user1_to_user2_state=RelationStateType.OK
            ).first()
            row_for_pended_member_ok_with_real_member = UserRelationsInRoom.objects.filter(
                user1=pended_id, user2=real_member_id, user1_to_user2_state=RelationStateType.OK
            ).first()
            if (row_for_real_member_ok_with_pended_member is None) or (
                    row_for_pended_member_ok_with_real_member is None):
                confirm = False
                break
        if confirm:
            serializer = Room_UserSerializers(room_user_row,
                                              data={"room": room.id, "user": pended_id, "user_state": StateType.OK})
            serializer.is_valid()
            serializer.save()
            message = "عضوی که شما تایید کردید تایید همه اعضای اتاق را گرفته است و همچنین اعضای تایید شده اتاق را تایید کرده است و به اتاق اضافه می‌شود."
            # TODO Response monaseb shamel pending inayeh jadid
        else:
            message = "عضوی که شما تایید کردید تایید همه اعضای اتاق را نگرفته است و یا همه اعضای تایید شده اتاق را تایید نکرده است و فعلا باید منتظر بماند."
            # TODO Response monaseb shamel pending inayeh jadid
    else:
        message = "اتاقی برای این کاربر ثبت نشده است!"
    return message


@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def get_waiting_users(request):
    user = request.user
    account = Account.objects.filter(user=user).first()
    row_for_user_in_room_user = Room_User.objects.filter(user=account.id).first()
    data = {"data": [], "message": ""}
    if row_for_user_in_room_user is None:
        data['not_request_for_room'] = True
        return Response(data, status=status.HTTP_200_OK)
    else:
        state_in_room = row_for_user_in_room_user.user_state
        waitingUsers = []
        if state_in_room == StateType.OK:
            waitingUsers1 = UserRelationsInRoom.objects.filter(user1=account.id,
                                                               user1_to_user2_state=RelationStateType.PENDING)
            waitingUsers2 = UserRelationsInRoom.objects.filter(user1=account.id,
                                                               user1_to_user2_state=RelationStateType.UNKNOWN)
            waitingUsers1.union(waitingUsers2)
            for w_u in waitingUsers1:
                waitingUser = Account.objects.filter(id=w_u.user2_id).first()
                waitingUsers.append(waitingUser)
        elif state_in_room == StateType.PENDING:
            room_id = row_for_user_in_room_user.room_id
            real_room_users_rows = Room_User.objects.filter(room=room_id, user_state=StateType.OK)
            waitingUsers = []
            for row in real_room_users_rows:
                real_user_id = row.user_id
                relation_between_owner_and_real_user_row = UserRelationsInRoom.objects.filter(user1=account.id,
                                                                                              user2=real_user_id,
                                                                                              user1_to_user2_state=RelationStateType.PENDING).first()
                if relation_between_owner_and_real_user_row is not None:
                    waitingUser = Account.objects.filter(id=real_user_id).first()
                    waitingUsers.append(waitingUser)
                relation_between_owner_and_real_user_row = UserRelationsInRoom.objects.filter(user1=account.id,
                                                                                              user2=real_user_id,
                                                                                              user1_to_user2_state=RelationStateType.UNKNOWN).first()
                if relation_between_owner_and_real_user_row is not None:
                    waitingUser = Account.objects.filter(id=real_user_id).first()
                    waitingUsers.append(waitingUser)

        print(waitingUsers)
        serializer = AccountSerializer(waitingUsers, many=True)
        data['data'] = serializer.data
        return Response(data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, ])
def delete_request(request):
    data = {"data": "", "message": ""}
    return Response(data)
