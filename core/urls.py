from django.contrib import admin
from django.urls import include, path, re_path

from apps.events.urls import events_router

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/events/', include(events_router.urls)),
    re_path(r'^auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.jwt')),
]
