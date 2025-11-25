from django.db import models


class Job(models.Model):
    """
    Oficios (plomero, electricista, etc.)
    Usa el mismo ID entero que en TROFI (Express/Firebase).
    """
    id = models.IntegerField(primary_key=True)  
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.id} - {self.name}"


class UserAnalytics(models.Model):
    """
    Usuario simplificado para analíticas.
    Usa el UID de Firebase / TROFI como primary key.
    """
    uid = models.CharField(max_length=100, primary_key=True) 
    name = models.CharField(max_length=255)
    email = models.EmailField()
    is_worker = models.BooleanField(default=False)
    created_at = models.DateTimeField()  #
    job = models.ForeignKey(
        Job,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="users",
    )

    def __str__(self):
        return f"{self.uid} - {self.name}"


class ReviewAnalytics(models.Model):
    """
    Reseñas utilizadas para calcular promedios.
    Usa el ID (key push) de TROFI como primary key.
    """
    id = models.CharField(max_length=100, primary_key=True)  
    reviewer = models.ForeignKey(
        UserAnalytics,
        related_name="reviews_given",
        on_delete=models.CASCADE,
    )
    reviewed = models.ForeignKey(
        UserAnalytics,
        related_name="reviews_received",
        on_delete=models.CASCADE,
    )
    score = models.PositiveSmallIntegerField()
    description = models.TextField()
    created_at = models.DateTimeField()  
    def __str__(self):
        return f"Review {self.id} ({self.score})"
