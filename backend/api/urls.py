from django.urls import path
from .views import ChatIAView

urlpatterns = [
    path('chat/', ChatIAView.as_view(), name='chat_ia'),
]