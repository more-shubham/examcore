"""URL configuration for examcore project."""

# from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

urlpatterns = [
    # path('admin/', admin.site.urls),
    path("", include("apps.accounts.urls", namespace="accounts")),
    path("exams/", include("apps.exams.urls", namespace="exams")),
    path("questions/", include("apps.questions.urls", namespace="questions")),
    path("results/", include("apps.results.urls", namespace="results")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
