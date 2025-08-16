from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('config/', admin.site.urls),
    path('jobs/', include('jobs.urls')),
    path('users/', include('users.urls')),
    path('', include('home.urls')),
    path('chatbot/', include('chatbot.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)