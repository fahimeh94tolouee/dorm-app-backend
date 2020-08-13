from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [
    path('register/', views.register),
    path('login/', views.login),
    path('token/refresh/', views.refresh_token),
    path('token/revoke/', views.revoke_token),
    path('account/', views.get_account),
    path('update_info/', views.update_account),
]