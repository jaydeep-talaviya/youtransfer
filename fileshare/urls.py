from django.urls import path
from .views import (register,login_request,logout_request,home,
                    update_profile,change_password,
                    success_uploaded_file,multifile_viewer,
                    download_file,download_single_file,
                    share_via_email,
                    users_files,file_shared_with_user,
                    delete_file)

from django.contrib.auth import views as auth_views

urlpatterns = [
    path('',home,name='home'),
    path('register', register,name='register'),
    path('login',login_request,name='login'),
    path('logout',logout_request,name='logout'),
    path('profile/update',update_profile,name='update_profile'),
    path('profile/change-password',change_password,name='change_password'),
    
    path('upload/success/<str:unique_file_num>',success_uploaded_file,name='success_uploaded'),
    path('upload/file/<str:unique_file_num>',multifile_viewer,name='multifile_viewer'),
    
    path('download/file/<str:unique_file_num>/download',download_file,name='download_file'),
    path('download/single/file/<str:doc_num>/download',download_single_file,name='download_single_file'),

    path('share/zip',share_via_email,name='share_via_email'),
    path('view/own/files',users_files,name='users_files'),
    path('view/files',file_shared_with_user,name='file_shared_with_user'),

    path('view/own/delete/<str:unique_file_num>',delete_file,name='delete_file'),
    # path('view/own/delete/single/<str:uuid_id>',delete_single_file,name='delete_file_upload'),


]
