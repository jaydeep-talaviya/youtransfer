import json
import os

from pytube import Playlist,YouTube
import threading
from youtransfer.celery import app
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def on_progress(stream, chunk, bytes_remaining,username,video_url):
    """Callback function"""
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    pct_completed = bytes_downloaded / total_size * 100
    print(f"Status: {round(pct_completed, 2)} %")
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "notification_" + username,
        {
            'type': 'send_notification',
            'message': json.dumps(
                {'message': f"{round(pct_completed, 2)} %",
                 "video_url":video_url
                 }
            ),
        }
    )


# Define a function to download a video
def download_video(video_url,username):
    yt = YouTube(video_url,on_progress_callback=lambda stream, chunk, bytes_remaining: on_progress(stream, chunk, bytes_remaining,username,video_url))
    stream = yt.streams.get_highest_resolution()

    title = stream.title
    file_extension = stream.mime_type.split('/')[1]

    homedir = os.path.expanduser("~")
    dirs = os.path.join(homedir, 'Downloads')

    stream.download(output_path=dirs, filename=f"{title}.{file_extension}")


@app.task
# Function to download videos from a playlist using multithreading
def download_playlist(playlist_url,username):
    playlist = Playlist(playlist_url)
    threads = []
    for video_url in playlist.video_urls:
        thread = threading.Thread(target=download_video, args=(video_url,username))
        thread.start()
        threads.append(thread)

    # Wait for all threads to finish
    for thread in threads:
        thread.join()