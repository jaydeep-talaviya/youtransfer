from django.urls import path
from .views import youtube_link_page,get_video_info,download_file

urlpatterns = [
    path('youtube/single',youtube_link_page,name='youtube_single_video'),
    path('youtube/single/info',get_video_info,name='youtube_single_video_info'),
    path('youtube/single/file/download',download_file,name='youtube_single_file_download'),
]