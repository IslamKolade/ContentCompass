from django.urls import path
from .views import *

app_name = 'content'

urlpatterns = [
    path("categories/", categories, name="categories"),
    path("categories/<int:id>/", category, name="category"),
    path("<int:id>/", content, name="content"),
    path("", contents, name="contents"),
    path("recommendations/", content_recommendations, name="content_recommendations"),
]