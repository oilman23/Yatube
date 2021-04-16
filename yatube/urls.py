from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404, handler500
from django.contrib import admin
from django.urls import include, path
import posts.views

handler404 = "posts.views.page_not_found"
handler500 = "posts.views.server_error"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("404/", posts.views.page_not_found, name="error404"),
    path("500/", posts.views.server_error, name="error500"),
    path("auth/", include("users.urls")),
    path("auth/", include("django.contrib.auth.urls")),
    path("", include("posts.urls")),
    path('about/', include('about.urls', namespace='about')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += (path("__debug__/", include(debug_toolbar.urls)),)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
