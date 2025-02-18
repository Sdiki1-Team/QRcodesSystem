from django.urls import path
from .views import RegisterView, LoginView, PingView, RefreshTokenView, LogoutView, StatusUser

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('ping/', PingView.as_view(), name='ping'),
    path('refresh/', RefreshTokenView.as_view(), name='refresh_token'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path("status/", StatusUser.as_view(), name="status"),
]
