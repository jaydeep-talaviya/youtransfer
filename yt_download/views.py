import os
from wsgiref.util import FileWrapper

from django.core.files import File
from django.http import FileResponse
from django.shortcuts import render,redirect,HttpResponse
from django.contrib import messages
from pytube import YouTube,Playlist

# Create your views here.

######### youtube ######
from yt_download.utils import download_playlist,on_progress


def youtube_link_page(request):
    return render(request,'yt_download/youtube_link_page.html')

def get_video_info(request):
    if request.method == "POST":
        try:
            url = request.POST.get('url')
            yt = YouTube(url)
            videos = []
            video_only = yt.streams.filter(mime_type="video/mp4")
            if video_only:
                for i in video_only:
                    vid_size = round(i.filesize/1024/1024, 1)
                    videos.append([i, vid_size])
            context = {'videos': videos, 'thumbnail': yt.thumbnail_url, 'title': yt.title, 'url': url}
            return render(request, 'yt_download/youtube_link_page.html', context)

        except Exception as e:
            messages.warning(request, "Not found! Please check the URL(Link)")
            return redirect(youtube_link_page)
    else:
        return redirect(youtube_link_page)



def download_file(request):
    if request.method == "POST":
        url = request.POST.get('url')
        itag = request.POST.get('itag')

        yt = YouTube(url,on_progress_callback=on_progress).streams.get_by_itag(itag)
        title = yt.title
        file_extension = yt.mime_type.split('/')[1]

        homedir = os.path.expanduser("~")
        dirs = os.path.join(homedir, 'Downloads')
        print(">>>>>11")
        yt.download(output_path=dirs, filename=f"{title}.{file_extension}")
        print(">>>>>22")
        file_path = os.path.join(dirs, f"{title}.{file_extension}")
        file = FileResponse(open(file_path, 'rb'), as_attachment=True)
        # os.remove(file_path)
        return file

def youtube_playlist_link_page(request):
    return render(request,'yt_download/youtube_playlist_link_page.html')


def get_playlist_videos(request):
    if request.method == "POST":
        try:
            url = request.POST.get('url')
            pl = Playlist(url)
            videos = []
            total_videos = len(pl)
            thumbnail_img=''
            try:
                thumbnail_img = pl.initial_data.get("microformat")['microformatDataRenderer'].get('thumbnail')['thumbnails'][-1].get('url')
            except Exception as e:
                pass

            for video in pl.videos:
                print(video)
                highest_clearity_video = video.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
                videos.append({
                    'itag':highest_clearity_video.itag,
                    'title':video.title,
                    'video_url':video.watch_url,
                    'thumbnail_url':video.thumbnail_url,
                    'size':round(highest_clearity_video.filesize/1024/1024, 1),
                })
            context = {'videos': videos, 'thumbnail': thumbnail_img, 'title': pl.title, 'url': url,'total_videos':total_videos}
            return render(request, 'yt_download/youtube_playlist_link_page.html', context)

        except Exception as e:
            print(">>>e",e)
            messages.warning(request, "Not found! Please check the URL(Link)")
            return redirect(youtube_link_page)
    else:
        return redirect(youtube_playlist_link_page)


def download_playlist_view(request):
    if request.method == 'POST':
        playlist_url = request.POST.get('playlist_url')
        if playlist_url:
            download_playlist(playlist_url)
            return HttpResponse('Downloading videos from the playlist. Please check your downloads folder.')

    return render(request, 'download_playlist.html')