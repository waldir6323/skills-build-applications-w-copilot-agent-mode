from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    ActivityLogViewSet,
    ClientRecordViewSet,
    GymUserViewSet,
    LeaderboardView,
    ProductViewSet,
    TeamViewSet,
    TrainingSuggestionViewSet,
)

router = DefaultRouter()
router.register(r'users', GymUserViewSet, basename='gymuser')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'clients', ClientRecordViewSet, basename='clientrecord')
router.register(r'teams', TeamViewSet, basename='team')
router.register(r'activities', ActivityLogViewSet, basename='activitylog')
router.register(r'suggestions', TrainingSuggestionViewSet, basename='trainingsuggestion')

urlpatterns = [
    path('', include(router.urls)),
    path('leaderboard/', LeaderboardView.as_view(), name='leaderboard'),
]
