from rest_framework import serializers
from .models import Job, UserAnalytics, ReviewAnalytics


# ===============================
# SERIALIZER: Job
# ===============================
class JobSyncSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ["id", "name"]


# ===============================
# SERIALIZER: UserAnalytics
# ===============================
class UserSyncSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnalytics
        fields = [
            "uid",
            "name",
            "email",
            "is_worker",
            "created_at",
            "job",
        ]


# ===============================
# SERIALIZER: ReviewAnalytics
# ===============================
class ReviewSyncSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewAnalytics
        fields = [
            "id",
            "reviewer",
            "reviewed",
            "score",
            "description",
            "created_at",
        ]
