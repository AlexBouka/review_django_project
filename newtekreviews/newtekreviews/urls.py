"""
URL configuration for newtekreviews project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path, include

from django.contrib.sitemaps.views import sitemap

from . import settings

from review.sitemaps import ReviewSitemap

sitemaps = {
    'published_reviews': ReviewSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('review.urls', namespace='review')),  # Review App urls
    path('auth/', include('users.urls', namespace='users')),  # Auth App urls
    path('api/v1/', include('newtek_api.urls', namespace='newtek_api')),  # NewTek API urls
    path('api/v1/s-auth/', include('rest_framework.urls')),
    path('api/v1/auth/', include('djoser.urls')),
    path('api/v1/auth/', include('djoser.urls.authtoken')),
    path('__debug__/', include('debug_toolbar.urls')),
    path('captcha/', include('captcha.urls')),
    path(
        'sitemap.xml', sitemap, {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap'),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
