import os

from django.http import FileResponse
from pytube import Playlist
import threading



def on_progress(stream, chunk, bytes_remaining):
    """Callback function"""
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    pct_completed = bytes_downloaded / total_size * 100
    print(f"Status: {round(pct_completed, 2)} %")


# Define a function to download a video
def download_video(video_url):
    from pytube import YouTube
    yt = YouTube(video_url,on_progress_callback=on_progress)
    stream = yt.streams.get_highest_resolution()

    title = stream.title
    file_extension = stream.mime_type.split('/')[1]

    homedir = os.path.expanduser("~")
    dirs = os.path.join(homedir, 'Downloads')
    print(">>>>>11")

    stream.download(output_path=dirs, filename=f"{title}.{file_extension}")
    print(">>>>>22")


# Function to download videos from a playlist using multithreading
def download_playlist(playlist_url):
    playlist = Playlist(playlist_url)
    threads = []
    for video_url in playlist.video_urls:
        thread = threading.Thread(target=download_video, args=(video_url,))
        thread.start()
        threads.append(thread)

    # Wait for all threads to finish
    for thread in threads:
        thread.join()