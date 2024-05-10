from django.urls import path

from .views import FolderPathView

urlpatterns = [
    path("media-library/folder-path", FolderPathView.as_view()),
]
