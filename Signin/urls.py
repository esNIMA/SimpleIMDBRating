from django.urls import path
from .views import SigninView, LoginView

urlpatterns = [
    path('signin/', SigninView.as_view(), name='signin'),
    path('login/', LoginView.as_view(), name='login'),
]