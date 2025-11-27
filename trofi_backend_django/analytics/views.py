from django.db.models.functions import TruncMonth
from django.db.models import Count, Avg, Q
from django.db import IntegrityError

from .models import UserAnalytics, Job, ReviewAnalytics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# ===========================
# SYNC VIEWS (EXPRESS a DJANGO)
# ===========================

class SyncJobView(APIView):
    def post(self, request):
        from .serializers import JobSyncSerializer
        serializer = JobSyncSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"ok": True, "message": "Job creado"}, status=201)
        return Response(serializer.errors, status=400)

    def put(self, request, pk):
        from .serializers import JobSyncSerializer
        try:
            job = Job.objects.get(pk=pk)
        except Job.DoesNotExist:
            return Response({"error": "Job no encontrado"}, status=404)

        serializer = JobSyncSerializer(job, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"ok": True, "message": "Job actualizado"})
        return Response(serializer.errors, status=400)



class SyncUserView(APIView):
    def post(self, request):
        from .serializers import UserSyncSerializer
        serializer = UserSyncSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"ok": True, "message": "Usuario creado"}, status=201)
        return Response(serializer.errors, status=400)

    def put(self, request, pk):
        from .serializers import UserSyncSerializer
        try:
            user = UserAnalytics.objects.get(pk=pk)
        except UserAnalytics.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=404)

        serializer = UserSyncSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"ok": True})
        return Response(serializer.errors, status=400)



class SyncReviewView(APIView):
    def post(self, request):
        from .serializers import ReviewSyncSerializer
        serializer = ReviewSyncSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"ok": True, "message": "Review creada"}, status=201)

        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        try:
            review = ReviewAnalytics.objects.get(pk=pk)
            review.delete()
            return Response({"ok": True, "message": "Review eliminada"})
        except ReviewAnalytics.DoesNotExist:
            return Response({"error": "Review no encontrada"}, status=404)



# ===========================
# ANALYTICS VIEWS (DJANGO a EXPRESS)
# ===========================

class UsersStatsView(APIView):
    """
    Estadísticas de usuarios
    """
    def get(self, request):
        try:
            total = UserAnalytics.objects.count()
            workers = UserAnalytics.objects.filter(is_worker=True).count()
            clients = total - workers

            # Usuarios por mes
            users_by_month = (
                UserAnalytics.objects
                .annotate(month=TruncMonth("created_at"))
                .values("month")
                .annotate(total=Count("uid"))
                .order_by("month")
            )

            formatted = [
                {
                    "month": item["month"].strftime("%Y-%m") if item["month"] else None,
                    "total": item["total"]
                }
                for item in users_by_month
                if item["month"]
            ]

            return Response({
                "success": True,
                "data": {
                    "total_users": total,
                    "workers": workers,
                    "clients": clients,
                    "users_by_month": formatted
                }
            })
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=500
            )


class WorkersStatsView(APIView):
    """
    Estadísticas de trabajadores
    """
    def get(self, request):
        try:
            # Trabajadores por oficio
            workers_by_job = (
                UserAnalytics.objects.filter(is_worker=True)
                .values("job__id", "job__name")
                .annotate(total=Count("uid"))
                .order_by("-total")
            )

            # Top trabajadores por puntuación
            top_workers = (
                UserAnalytics.objects.filter(is_worker=True)
                .annotate(avg_score=Avg("reviews_received__score"))
                .filter(avg_score__isnull=False)  # Solo con reseñas
                .order_by("-avg_score")[:10]
            )

            top_list = [
                {
                    "uid": w.uid,
                    "name": w.name,
                    "job": w.job.name if w.job else None,
                    "avg_score": round(float(w.avg_score or 0), 2)
                }
                for w in top_workers
            ]

            return Response({
                "success": True,
                "data": {
                    "workers_by_job": list(workers_by_job),
                    "top_workers": top_list
                }
            })
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=500
            )


class ReviewsStatsView(APIView):
    """
    Estadísticas de reseñas
    """
    def get(self, request):
        try:
            # Promedio global
            global_avg = ReviewAnalytics.objects.aggregate(avg=Avg("score"))["avg"] or 0

            # Promedio por oficio
            avg_by_job = (
                ReviewAnalytics.objects
                .values("reviewed__job__name")
                .annotate(avg_score=Avg("score"))
                .order_by("reviewed__job__name")
            )

            # Total de reseñas
            total_reviews = ReviewAnalytics.objects.count()

            # Distribución de scores
            score_distribution = (
                ReviewAnalytics.objects
                .values("score")
                .annotate(count=Count("id"))
                .order_by("score")
            )

            return Response({
                "success": True,
                "data": {
                    "global_average": round(float(global_avg), 2),
                    "total_reviews": total_reviews,
                    "average_by_job": list(avg_by_job),
                    "score_distribution": list(score_distribution)
                }
            })
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=500
            )