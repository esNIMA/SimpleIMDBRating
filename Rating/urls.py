from django.urls import path
from .views import CriticView

urlpatterns = [path('critics/', CriticView.as_view(), name='critics')]