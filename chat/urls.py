from django.urls import path
from .views import chat_page, chat_api, logs_view, process_audio

urlpatterns = [
    path("", chat_page, name="chat_page"),
    path("api/", chat_api, name="chat_api"),
    path("logs/", logs_view, name="logs"),
    path("process_audio/", process_audio, name="process_audio"),
]
