from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.sitemaps.views import sitemap
from djangoBlogApp.sitemaps import PostSitemap
from django.views.static import serve

sitemaps = {
    "posts": PostSitemap,
}

admin.site.site_url = '/blog'

urlpatterns = [
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
]

"""if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)"""