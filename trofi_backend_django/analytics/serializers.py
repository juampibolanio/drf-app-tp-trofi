from rest_framework import serializers
from .models import Job, UserAnalytics, ReviewAnalytics
from decimal import Decimal


# ===============================
# SERIALIZER: Job
# ===============================

class JobSyncSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ["id", "firebase_key", "name"]

    def validate(self, data):
        if not data.get("name"):
            raise serializers.ValidationError({"name": "El nombre no puede estar vacío"})
        if not data.get("firebase_key"):
            raise serializers.ValidationError({"firebase_key": "Falta firebase_key"})
        return data


# ===============================
# SERIALIZER: UserAnalytics
# ===============================

class UserSyncSerializer(serializers.ModelSerializer):
    """
    job llega como firebase_key desde Express.
    Acá lo convertimos a la FK correcta ANTES de validar.
    """

    job = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = UserAnalytics
        fields = "__all__"

    def to_internal_value(self, data):
        """
        Convertir firebase_key → Job instance ANTES de validación.
        """
        data = data.copy()

        job_key = data.get("job")

        if job_key:
            try:
                job = Job.objects.get(firebase_key=job_key)
                data["job"] = job.pk   # convertir a PK real
            except Job.DoesNotExist:
                raise serializers.ValidationError({
                    "job": "El job no existe en Django. Debes sincronizar Jobs primero."
                })
        else:
            data["job"] = None

        return super().to_internal_value(data)


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

    def validate_score(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("El score debe estar entre 1 y 5")
        decimal_value = Decimal(str(value))
        if (decimal_value * 2) % 1 != 0:
            raise serializers.ValidationError("El score debe ser múltiplo de 0.5")
        return value

    def validate(self, data):
        if data["reviewer"] == data["reviewed"]:
            raise serializers.ValidationError("No puedes reseñarte a ti mismo.")
        return data
