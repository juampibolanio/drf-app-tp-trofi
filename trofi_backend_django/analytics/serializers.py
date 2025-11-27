from rest_framework import serializers
from .models import Job, UserAnalytics, ReviewAnalytics
from decimal import Decimal


# ===============================
# SERIALIZER: Job
# ===============================
class JobSyncSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ["id", "name"]

    def validate_name(self, value):
        """Validar que el nombre no esté vacío"""
        if not value or not value.strip():
            raise serializers.ValidationError("El nombre del oficio no puede estar vacío")
        return value.strip()


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

    def validate_uid(self, value):
        """Validar que el UID no esté vacío"""
        if not value or not value.strip():
            raise serializers.ValidationError("El UID no puede estar vacío")
        return value.strip()

    def validate_email(self, value):
        """Validar formato de email"""
        if not value or '@' not in value:
            raise serializers.ValidationError("Email inválido")
        return value.lower().strip()


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
        """
        Validar que el score esté entre 1 y 5 
        y sea múltiplo de 0.5 (permite medias estrellas)
        """
        if value < 1 or value > 5:
            raise serializers.ValidationError("El score debe estar entre 1 y 5")
        
        # Convertir a Decimal para validación precisa
        decimal_value = Decimal(str(value))
        
        # Validar que sea múltiplo de 0.5
        if (decimal_value * 2) % 1 != 0:
            raise serializers.ValidationError(
                "El score debe ser en incrementos de 0.5 (ej: 1, 1.5, 2, 2.5, etc.)"
            )
        
        return value

    def validate_description(self, value):
        """Validar longitud de descripción"""
        if not value or not value.strip():
            raise serializers.ValidationError("La descripción no puede estar vacía")
        
        if len(value.strip()) < 10:
            raise serializers.ValidationError("La descripción debe tener al menos 10 caracteres")
        
        if len(value) > 500:
            raise serializers.ValidationError("La descripción no puede exceder 500 caracteres")
        
        return value.strip()

    def validate(self, data):
        """Validación a nivel de objeto"""
        # Validar que reviewer y reviewed no sean el mismo
        if data.get('reviewer') == data.get('reviewed'):
            raise serializers.ValidationError("No puedes reseñarte a ti mismo")
        
        return data