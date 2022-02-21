from __future__ import unicode_literals
import youtube_dl

def download_video_to_mp3(url):
    video_info = youtube_dl.YoutubeDL().extract_info(url, download=False)
    video_download_path = f'multimedia/{video_info["title"]}.mp3'
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': video_download_path
    }
    print(f"Video url to download: {url}")

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    print('test')
    return video_download_path