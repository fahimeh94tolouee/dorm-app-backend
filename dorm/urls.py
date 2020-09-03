from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [
    path('request/<int:room_id>/', views.request_room),
    path('answer/', views.answer_user),
    path('rooms/', views.get_rooms),
    path('rooms/<int:room_id>/', views.get_room_info),
    path('waiting_users/', views.get_waiting_users),
    path('user_relations/', views.get_user_relation),
]