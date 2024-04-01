"""youtransfer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import path,include,re_path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('fileshare.urls')),
    re_path(r'^password_reset/$', auth_views.PasswordResetView.as_view(),
            {'template_name': "registration/password_reset_form.html"},
            name='password_reset'),
    re_path(r'^password_reset/done/$', auth_views.PasswordResetDoneView.as_view(),
            {'template_name': "registration/password_reset_done.html"},
            name='password_reset_done'),
    path('^reset/<str:uidb64>/<str:token>/',
            auth_views.PasswordResetConfirmView.as_view(),
            {'template_name': "registration/password_reset_confirm.html"},
            name='password_reset_confirm'),
    re_path(r'^reset/done/$', auth_views.PasswordResetCompleteView.as_view(),
            {'template_name': "registration/password_reset_complete.html"},
            name='password_reset_complete'),

]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler400 = 'fileshare.views.bad_request'
handler403 = 'fileshare.views.permission_denied'
handler404 = 'fileshare.views.page_not_found'
handler500 = 'fileshare.views.server_error'