from django.db import models


class Job(models.Model):
    """
    Oficios sincronizados desde Firebase/Express.
    firebase_key = ID real de Firebase (-Oew_...)
    id = autoincremental local en Django.
    """
    name = models.CharField(max_length=100)
    firebase_key = models.CharField(max_length=200, unique=True, default="")

    class Meta:
        db_table = 'analytics_job'

    def __str__(self):
        return f"{self.id} - {self.name}"


class UserAnalytics(models.Model):
    """
    Usuarios sincronizados desde Firebase.
    uid = UID real de Firebase.
    job = FK a Job.
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
        indexes = [
            models.Index(fields=['is_worker']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.uid} - {self.name}"


class ReviewAnalytics(models.Model):
    """
    Reseñas sincronizadas desde Firebase.
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
    score = models.DecimalField(max_digits=2, decimal_places=1)
    description = models.TextField()
    created_at = models.DateTimeField()

    class Meta:
        db_table = 'analytics_review'
        indexes = [
            models.Index(fields=['score']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Review {self.id} ({self.score}★)"
