from django.db import models


class Job(models.Model):
    """
    Oficios (plomero, electricista, etc.)
    Usa el mismo ID entero que en TROFI (Express/Firebase).
    """
    id = models.IntegerField(primary_key=True)  
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'analytics_job'
        verbose_name = 'Oficio'
        verbose_name_plural = 'Oficios'

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
    created_at = models.DateTimeField()
    job = models.ForeignKey(
        Job,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="users",
    )

    class Meta:
        db_table = 'analytics_user'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        indexes = [
            models.Index(fields=['is_worker']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.uid} - {self.name}"


class ReviewAnalytics(models.Model):
    """
    Reseñas utilizadas para calcular promedios.
    Usa el ID (key push) de TROFI como primary key.
    Soporta scores decimales (1, 1.5, 2, 2.5, etc.)
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
    score = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        help_text="Puntuación de 1.0 a 5.0 (permite medias estrellas)"
    )
    description = models.TextField()
    created_at = models.DateTimeField()

    class Meta:
        db_table = 'analytics_review'
        verbose_name = 'Reseña'
        verbose_name_plural = 'Reseñas'
        indexes = [
            models.Index(fields=['score']),
            models.Index(fields=['created_at']),
            models.Index(fields=['reviewer']),
            models.Index(fields=['reviewed']),
        ]

    def __str__(self):
        return f"Review {self.id} ({self.score}★)"