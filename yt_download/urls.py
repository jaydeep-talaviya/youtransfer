from django.urls import path
from .views import (youtube_link_page,get_video_info,
                    download_file,youtube_playlist_link_page,
                    get_playlist_videos,download_playlist_view)

urlpatterns = [
    path('youtube/single',youtube_link_page,name='youtube_single_video'),
    path('youtube/single/info',get_video_info,name='youtube_single_video_info'),
    path('youtube/single/file/download',download_file,name='youtube_single_file_download'),

    path('youtube/multi/file',youtube_playlist_link_page,name='youtube_multi_video'),
    path('youtube/multi/info', get_playlist_videos, name='youtube_multi_video_info'),
    path('youtube/multi/download', download_playlist_view, name='download_playlist_videos'),

]