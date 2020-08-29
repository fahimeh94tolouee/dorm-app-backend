from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
import requests
from .serializers import RoomsSerializers, Room_UserSerializers, UserRelationsInRoomSerializers
from accounts.models import Account
from accounts.serializers import AccountSerializer
from .models import Room, Room_User, UserRelationsInRoom, StateType, RelationStateType
from message.serializers import LogMessageSerializers
from message.models import MessageType


def getRooms(user):
    account = Account.objects.filter(user=user).first()
    row_for_user_in_room_user = Room_User.objects.filter(user=account.id).first()
    rooms = Room.objects.all()
    roomsArray = []
    for room in rooms:
        _data = RoomsSerializers(room).data
        if (row_for_user_in_room_user is not None) and (room.id == row_for_user_in_room_user.room_id):
            _data['my_status'] = row_for_user_in_room_user.user_state.value
        roomsArray.append(_data)
    serializer = RoomsSerializers(roomsArray, many=True)
    return serializer.data


@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def get_rooms(request):
    user = request.user
    data = getRooms(user)
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def get_room_info(request, room_id):
    user = request.user
    account = Account.objects.filter(user=user).first()
    rows_for_room_in_room_user = Room_User.objects.filter(room=room_id)
    serializer = Room_UserSerializers(rows_for_room_in_room_user, many=True)
    return Response(data=serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated, ])
def request_room(request, room_id):
    room = Room.objects.filter(id=room_id).first()
    finalData = {"message": "", "data": []}
    responseStatus = status.HTTP_200_OK
    user = request.user
    isAddRequest = request.data["is_add"]
    if room is not None:
        account = Account.objects.filter(user=user).first()
        userRoomArray = Room_User.objects.filter(user=account)
        if isAddRequest:
            userRoom = userRoomArray.first()
            if userRoom is None:
                roomWithUsers = Room_User.objects.filter(room_id=room_id)
                roomMembersNum = len(roomWithUsers)
                if roomMembersNum == 0:
                    serializer = Room_UserSerializers(
                        data={"user": account.id, "room": room.id, "user_state": StateType.OK})
                    if serializer.is_valid():
                        serializer.save()
                        finalData["message"] = "به اتاق اضافه شدید."
                    else:
                        print(serializer.errors, "CCC")
                        finalData["message"] = "دیتا ناصحیح است."
                        responseStatus = status.HTTP_400_BAD_REQUEST
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
                        finalData["message"] = "درخواست شما ارسال شد."
                    else:
                        finalData["message"] = "ظرفیت اتاق تکمیل است."
                        responseStatus = status.HTTP_400_BAD_REQUEST
            else:
                state = userRoom.user_state
                user_room = userRoom.room
                text = ""
                print(user_room, state, "PP")
                if state == StateType.OK:
                    text = " به عنوان عضو "
                elif state == StateType.PENDING:
                    text = " به عنوان منتظر "
                finalData["message"] = "شما در اتاق " + str(user_room) + text + "ثبت شده‌اید."
                responseStatus = status.HTTP_400_BAD_REQUEST
        else:
            if userRoomArray.first():
                userRoomArray.delete()
                UserRelationsInRoom.objects.filter(user1=account).delete()
                UserRelationsInRoom.objects.filter(user2=account).delete()
                finalData["message"] = "با موفقیت از اتاق " + str(room) + " حذف شدید."
            else:
                finalData["message"] = "شما از اعضای اتاق " + str(room) + " نمی‌باشید."
                responseStatus = status.HTTP_404_NOT_FOUND

    else:
        finalData["message"] = "شما در اتاق ""اتاق مورد نظر پیدا نشد."
        responseStatus = status.HTTP_404_NOT_FOUND
    finalData["data"] = getRooms(user)
    return Response(finalData, status=responseStatus)


# @api_view(['DELETE'])
# @permission_classes([IsAuthenticated, ])
# def delete_request(request):
#     data = {"data": "", "message": ""}
#     return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, ])
def answer_user(request):
    message = ""
    logMessageForPendedUser = ""
    responseStatus = status.HTTP_200_OK
    answer = request.data['answer']  # true or false
    pended_account_id = request.data['pended_account_id']
    responder_user_id = request.user
    responder_account = Account.objects.filter(user=responder_user_id).first()
    pended_account = Account.objects.filter(id=pended_account_id).first()
    rowForPendedAccountAndRespondedAccountInRelationTable1 = UserRelationsInRoom.objects.filter(
        user1=responder_account,
        user2=pended_account,
        user1_to_user2_state=RelationStateType.PENDING
    )
    rowForPendedAccountAndRespondedAccountInRelationTable2 = UserRelationsInRoom.objects.filter(
        user1=responder_account,
        user2=pended_account,
        user1_to_user2_state=RelationStateType.UNKNOWN
    )
    rowForPendedAccountAndRespondedAccountInRelationTable = rowForPendedAccountAndRespondedAccountInRelationTable1.union(
        rowForPendedAccountAndRespondedAccountInRelationTable2).first()
    if (pended_account is not None) and (rowForPendedAccountAndRespondedAccountInRelationTable is not None):
        room_user_row = Room_User.objects.filter(user=pended_account).first()
        room_user_row_confirm = Room_User.objects.filter(user=responder_account).first()
        if (room_user_row is not None) and (room_user_row.room == room_user_row_confirm.room):
            room = room_user_row.room
            if answer:
                data = {"user1": responder_account.id, "user2": pended_account_id,
                        "user1_to_user2_state": RelationStateType.OK}
                serializer = UserRelationsInRoomSerializers(rowForPendedAccountAndRespondedAccountInRelationTable,
                                                            data=data)
                serializer.is_valid()
                serializer.save()
                message = checkAddToRoom(pended_account_id, room_user_row, room)
                logMessageForPendedUser = 'شما توسط کاربر ' + str(
                    responder_account.user) + ' برای عضویت در اتاق ' + str(room) + ' تایید شدید.'
            else:

                logMessageForPendedUser = 'شما توسط کاربر ' + str(
                    responder_account.user) + ' برای عضویت در اتاق ' + str(room) + ' رد شدید.'
                rowForRoom.delete()
                UserRelationsInRoom.objects.filter(user1=pended_account).delete()
                UserRelationsInRoom.objects.filter(user2=pended_account).delete()
                message = "رد فرد مورد نظر با موفقیت انجام شد."

            logMessageSerializer = LogMessageSerializers(
                data={"user": pended_account.id, "message": logMessageForPendedUser, "type": MessageType.REJECT})
            logMessageSerializer.is_valid()
            print(logMessageSerializer.errors, "Seria Log M error")
            logMessageSerializer.save()
        else:
            message = "کاربر مورد نظر و شما در اتاق یکسانی قرار ندارید!"
            responseStatus = status.HTTP_404_NOT_FOUND
    else:
        message = "کاربر مورد نظر شما یافت نشد!"
        responseStatus = status.HTTP_404_NOT_FOUND
    # room_user_row = Room_User.objects.filter(user=pended_account_id).first()
    # all_corresponding_room_user_rows = Room_User.objects.filter(room=room_user_row.room.id)
    # all_user_with_state = Account.objects.filter(id__in=all_corresponding_room_user_rows.values('user_id'))
    # print(all_user_with_state, "TTTT")
    # membersListSerializer = Room_UserSerializers(list(all_corresponding_room_user_rows), many=True)
    # data = {"data": membersListSerializer.data, "message": message}
    data = getWaitingUsers(responder_user_id)
    data["message"] = message
    return Response(data, status=responseStatus)


def checkAddToRoom(pended_id, room_user_row, room):
    message = ""
    # room_user_row = Room_User.objects.filter(user=pended_id).first()
    # room_user_row_confirm = Room_User.objects.filter(user=responder_id).first()
    # if (room_user_row_confirm is not None) and (room_user_row.room == room_user_row_confirm.room):
        # room = room_user_row.room
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
        logMessageForPendedUser = 'شما توسط همه‌ی اعضای اتاق ' + str(room) + ' تایید شدید و به اتاق اضاقه شدید.'
        logMessageSerializer = LogMessageSerializers(
            data={"user": pended_id, "message": logMessageForPendedUser, "type": MessageType.REJECT})
        logMessageSerializer.is_valid()
        print(logMessageSerializer.errors, "Seria Log M error11")
        logMessageSerializer.save()
    else:
        message = "عضوی که شما تایید کردید تایید همه اعضای اتاق را نگرفته است و یا همه اعضای تایید شده اتاق را تایید نکرده است و فعلا باید منتظر بماند."

    # else:
    #     message = "اتاقی برای این کاربر ثبت نشده است!"
    return message


@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def get_waiting_users(request):
    user = request.user
    data = getWaitingUsers(user)
    return Response(data)


def getWaitingUsers(user):
    account = Account.objects.filter(user=user).first()
    row_for_user_in_room_user = Room_User.objects.filter(user=account).first()
    data = {"data": {"is_in_room": False, "data": []}, "message": ""}
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
            waitingUsersT = waitingUsers1.union(waitingUsers2)
            for w_u in waitingUsersT:
                waitingUser = Account.objects.filter(id=w_u.user2_id).first()
                waitingUsers.append(waitingUser)
            data["data"]["is_in_room"] = True
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
            data["data"]["is_in_room"] = False

        serializer = AccountSerializer(waitingUsers, many=True)
        data['data']["data"] = serializer.data
    return data
