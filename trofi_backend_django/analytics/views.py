from django.db.models.functions import TruncMonth
from django.db.models import Count, Avg

from .models import UserAnalytics, Job, ReviewAnalytics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# ===========================
# 🎯 SYNC VIEWS (EXPRESS → DJANGO)
# ===========================

class SyncJobView(APIView):
    def post(self, request):
        """
        Crear oficio desde Express
        """
        from .serializers import JobSyncSerializer
        serializer = JobSyncSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"ok": True}, status=201)
        return Response(serializer.errors, status=400)

    def put(self, request, pk):
        """
        Actualizar oficio desde Express
        """
        from .models import Job
        from .serializers import JobSyncSerializer

        try:
            job = Job.objects.get(pk=pk)
        except Job.DoesNotExist:
            return Response({"error": "Job not found"}, status=404)

        serializer = JobSyncSerializer(job, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"ok": True})
        return Response(serializer.errors, status=400)


class SyncUserView(APIView):
    def post(self, request):
        """
        Crear usuario desde Express
        """
        from .serializers import UserSyncSerializer
        serializer = UserSyncSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"ok": True}, status=201)
        return Response(serializer.errors, status=400)

    def put(self, request, pk):
        """
        Actualizar usuario desde Express
        """
        from .models import UserAnalytics
        from .serializers import UserSyncSerializer

        try:
            user = UserAnalytics.objects.get(pk=pk)
        except UserAnalytics.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        serializer = UserSyncSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"ok": True})
        return Response(serializer.errors, status=400)


class SyncReviewView(APIView):
    def post(self, request):
        """
        Crear review desde Express
        """
        from .serializers import ReviewSyncSerializer
        serializer = ReviewSyncSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"ok": True}, status=201)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        """
        Eliminar review desde Express
        """
        try:
            ReviewAnalytics.objects.get(pk=pk).delete()
        except ReviewAnalytics.DoesNotExist:
            return Response({"error": "Review not found"}, status=404)

        return Response({"ok": True})


# ===========================
# 📊 ANALYTICS VIEWS (DJANGO → EXPRESS)
# ===========================

class UsersStatsView(APIView):
    def get(self, request):
        total = UserAnalytics.objects.count()
        workers = UserAnalytics.objects.filter(is_worker=True).count()
        clients = total - workers

        users_by_month = (
            UserAnalytics.objects
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(total=Count("uid"))
            .order_by("month")
        )

        formatted = [
            {
                "month": item["month"].strftime("%Y-%m"),
                "total": item["total"]
            }
            for item in users_by_month
            if item["month"]
        ]

        return Response({
            "total_users": total,
            "workers": workers,
            "clients": clients,
            "users_by_month": formatted
        })


class WorkersStatsView(APIView):
    def get(self, request):
        workers_by_job = (
            UserAnalytics.objects.filter(is_worker=True)
            .values("job__id", "job__name")
            .annotate(total=Count("uid"))
            .order_by("-total")
        )

        top_workers = (
            UserAnalytics.objects.filter(is_worker=True)
            .annotate(avg_score=Avg("reviews_received__score"))
            .order_by("-avg_score")[:10]
        )

        top_list = [
            {
                "uid": w.uid,
                "name": w.name,
                "job": w.job.name if w.job else None,
                "avg_score": round(w.avg_score or 0, 2)
            }
            for w in top_workers
        ]

        return Response({
            "workers_by_job": workers_by_job,
            "top_workers": top_list
        })


class ReviewsStatsView(APIView):
    def get(self, request):
        global_avg = ReviewAnalytics.objects.aggregate(avg=Avg("score"))["avg"] or 0

        avg_by_job = (
            ReviewAnalytics.objects
            .values("reviewed__job__name")
            .annotate(avg_score=Avg("score"))
            .order_by("reviewed__job__name")
        )

        return Response({
            "global_average": round(global_avg, 2),
            "average_by_job": avg_by_job
        })
