from django.urls import path
from .views import (
    UsersStatsView,
    WorkersStatsView,
    ReviewsStatsView,

    SyncJobView,
    SyncUserView,
    SyncReviewView,
)

urlpatterns = [
    # === SYNC ===
    path("sync/jobs/", SyncJobView.as_view()),
    path("sync/jobs/<int:pk>/", SyncJobView.as_view()),
    path("sync/users/", SyncUserView.as_view()),
    path("sync/users/<str:pk>/", SyncUserView.as_view()),
    path("sync/reviews/", SyncReviewView.as_view()),
    path("sync/reviews/<str:pk>/", SyncReviewView.as_view()),

    # === ANALYTICS ===
    path("analytics/users/", UsersStatsView.as_view()),
    path("analytics/workers/", WorkersStatsView.as_view()),
    path("analytics/reviews/", ReviewsStatsView.as_view()),
]
