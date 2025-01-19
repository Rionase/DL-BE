from django.urls import path
from .views import RegisterView, LoginView, AdminView, GetMeView

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('login', LoginView.as_view(), name='login'),
    path('admin', AdminView.as_view(), name='admin'),
    path('get-me', GetMeView.as_view(), name='get-me'),
]
