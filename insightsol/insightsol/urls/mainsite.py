from django.urls import path
from mainsite.api import controllers as mainsite_api_views


urlpatterns = [
    path("api/<int:version>/bookLibrary",mainsite_api_views.GetLibraryAPI.as_view()),
]
