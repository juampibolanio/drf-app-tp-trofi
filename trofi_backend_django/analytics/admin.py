from django.contrib import admin
from .models import Job, UserAnalytics, ReviewAnalytics

# Register your models here.
admin.site.register(Job)
admin.site.register(UserAnalytics)
admin.site.register(ReviewAnalytics)