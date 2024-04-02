import os
from wsgiref.util import FileWrapper

from django.core.files import File
from django.http import FileResponse
from django.shortcuts import render,redirect,HttpResponse
from django.contrib import messages
from pytube import YouTube
# Create your views here.

######### youtube ######

def youtube_link_page(request):
    return render(request,'yt_download/youtube_link_page.html')

def get_video_info(request):
    if request.method == "POST":
        try:
            url = request.POST.get('url')
            yt = YouTube(url)
            videos = []
            audios = []
            video_only = yt.streams.filter(progressive=True)
            audio_only = yt.streams.filter(abr='128kbps', only_audio=True)
            if video_only:
                for i in video_only:
                    vid_size = round(i.filesize/1024/1024, 1)
                    videos.append([i, vid_size])
            if audio_only:
                audios.append(audio_only[0])
                audios.append(round(audio_only[0].filesize/1024/1024, 1))
            context = {'videos': videos, 'audios': audios, 'thumbnail': yt.thumbnail_url, 'title': yt.title, 'url': url}
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

        yt = YouTube(url).streams.get_by_itag(itag)
        title = yt.title
        file_extension = yt.mime_type.split('/')[1]

        homedir = os.path.expanduser("~")
        dirs = os.path.join(homedir, 'Downloads')

        if yt.type != 'audio':
            # yt.download(output_path=dirs, filename=f"{title}.mp4")
            # # Get the file path of the downloaded video
            # file_path = os.path.join(dirs, f"{title}.mp4")

            # Open the downloaded file as a Django File object
            # with open(file_path, 'rb') as file:
                # file_wrapper = File(file)
                # file_wrapper.name = file_wrapper.name.replace("." + file_extension, "") + "_yt" + "." + file_extension
                # Create an HTTP response with the file as attachment
                # response = HttpResponse(file_wrapper, content_type=f'video/{file_extension}')
                # response['Content-Disposition'] = f'attachment; filename="{file_wrapper.name}"'
                #
                # # Remove the downloaded file from the server
                # os.remove(file_path)
                #
                # return response

            return FileResponse(open(yt.download(skip_existing=True,output_path=dirs  ), 'rb'),as_attachment=True)


        else:
            yt.download(output_path=dirs, filename=f"{yt.title}.mp3")
            file_path = os.path.join(dirs, f"{title}.mp3")
            file = FileWrapper(open(file_path, 'rb'))
            response = HttpResponse(file, content_type='application/audio.mp3')
            response['Content-Disposition'] = f'attachment; filename = "{title}.mp3"'
            os.remove(file_path)
            return response