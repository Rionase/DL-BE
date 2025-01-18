from django.urls import path
from .views import RegisterView, LoginView, AdminView, RefreshTokenView, LogoutView

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('login', LoginView.as_view(), name='login'),
    path('admin', AdminView.as_view(), name='admin'),
    path('refresh', RefreshTokenView.as_view(), name='refresh-token'),
    path('logout', LogoutView.as_view(), name='logout'),
]
