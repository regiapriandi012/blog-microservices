from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from .feeds import LatestPostsFeed

urlpatterns = [
    path("feed/rss", LatestPostsFeed(), name="post_feed"),
]