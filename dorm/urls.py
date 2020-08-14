from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [
    path('request/<int:room_id>/', views.request_room),
    path('answer/<int:user_id>/', views.answer_user),
    path('rooms/', views.get_rooms),
    path('pended_users/', views.get_pended_user),
]