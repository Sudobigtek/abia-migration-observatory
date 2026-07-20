from django.urls import path
from .views import throttle_stats, my_rate_limit

urlpatterns = [
    path("stats/", throttle_stats, name="throttle-stats"),
    path("my-limit/", my_rate_limit, name="throttle-my-limit"),
]