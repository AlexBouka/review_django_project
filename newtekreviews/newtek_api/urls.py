from django.urls import path, include
from rest_framework import routers
from drf_spectacular.views import SpectacularAPIView

from .views import (
    ReviewTopicDetailAPIView,
    ReviewViewSet,
    CategoryViewSet,
)

app_name = 'newtek_api'

router = routers.DefaultRouter()
router.register(r'reviews', ReviewViewSet)  # basename parameter not specified as it is taken from the queryset
router.register(r'categories', CategoryViewSet)


urlpatterns = [
    path('', include(router.urls)),

    path('review-topic/<slug:topic_slug>/', ReviewTopicDetailAPIView.as_view()),

    path('schema/', SpectacularAPIView.as_view(), name='schema'),
]
