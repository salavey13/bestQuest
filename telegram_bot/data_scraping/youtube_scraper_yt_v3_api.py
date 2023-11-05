#Sure! Here's a function that takes a playlist URL as input, checks each video in the playlist for subtitle presence and best moments, calculates a rating value based on the view count speed and subscriber count, and returns a sorted list of links to the best moments along with the chapter names containing these moments:

import requests
import json
import base64
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs
import os
YTAPIKEY=os.environ["YouTube_Data_API_KEY"]
#print(YTAPIKEY)
def get_playlist_videos(playlist_url):
    playlist_id = parse_qs(urlparse(playlist_url).query).get('list')
    if not playlist_id:
        print("Invalid playlist URL")
        return []
    print(playlist_id)
    videos_url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults=50&playlistId={playlist_id}&key={YTAPIKEY}"
    try:
        videos_response = requests.get(videos_url)
    except Exception as e:
        print(e)
    videos_data = json.loads(videos_response.text)
    print(videos_data)
    videos = videos_data.get('items', [])
    video_list = []

    for video in videos:
        video_id = video['snippet']['resourceId']['videoId']
        video_info = get_video_info(video_id)
        subtitles_present = check_subtitles(video_id)
        best_moments = get_best_moments(video_id)

        video_list.append({
            'video_id': video_id,
            'title': video_info['title'],
            'subtitles_present': subtitles_present,
            'best_moments': best_moments,
            'view_count': video_info['view_count'],
            'subscriber_count': video_info['subscriber_count'],
        })

    sorted_video_list = sorted(video_list, key=lambda x: calculate_rating(x['view_count'], x['subscriber_count']), reverse=True)
    return sorted_video_list


def get_video_info(video_id):
    video_url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={YTAPIKEY}"
    video_response = requests.get(video_url)
    video_data = json.loads(video_response.text)

    video_info = video_data['items'][0]['snippet']
    statistics = video_data['items'][0]['statistics']

    title = video_info['title']
    view_count = int(statistics['viewCount'])
    subscriber_count = int(statistics.get('subscriberCount', 0))

    return {
        'title': title,
        'view_count': view_count,
        'subscriber_count': subscriber_count,
    }


def check_subtitles(video_id):
    subtitles_url = f"https://www.googleapis.com/youtube/v3/captions?part=id&videoId={video_id}&key={YTAPIKEY}"
    subtitles_response = requests.get(subtitles_url)
    subtitles_data = json.loads(subtitles_response.text)
    
    return bool(subtitles_data.get('items'))


def get_best_moments(video_id):
    best_moment_url = f"https://yt.lemnoslife.com/videos?part=mostReplayed&id={video_id}"
    page_best_moment_url = requests.get(best_moment_url)
    best_dict = json.loads(page_best_moment_url.text)
    
    best_moments = []

    if best_dict['items'][0]['mostReplayed'] is not None and n == 2:
        for moment in best_dict['items'][0]['mostReplayed']['timedMarkerDecorations']:
            timestamp = moment['visibleTimeRangeStartMillis']
            chapter_name, chapter_start, chapter_end = extract_best_chapter(page_info.text, timestamp)

            best_moments.append({
                'timestamp': timestamp / 1000,
                'chapter_name': chapter_name,
                'chapter_start': chapter_start,
                'chapter_end': chapter_end
            })

    return best_moments


def calculate_rating(view_count, subscriber_count):
    time_since_upload = timedelta(days=7)  # The time since the video was uploaded, adjust as per your requirement
    view_count_speed = view_count / time_since_upload.total_seconds()
    rating_value = view_count_speed * subscriber_count

    return rating_value


# Usage
playlist_url = "https://youtube.com/playlist?list=PLzKJi2GjpkEHbv_b8C_XKs0VT5T3cCraH"
playlist_videos = get_playlist_videos(playlist_url)

for video in playlist_videos:
    print("Video:", video['title'])
    print("Subtitles Present:", video['subtitles_present'])
    print("Best Moments:")
    for moment in video['best_moments']:
        print(f"Timestamp: {moment['timestamp']}, Chapter Name: {moment['chapter_name']}")
    print("------")

#Make sure to replace YTAPIKEY and <your_playlist_id> with your own YouTube API key and the ID of the playlist you want to analyze.

#This function retrieves the videos from the playlist, checks for subtitles presence, gets the best moments, calculates the rating value based on view count speed and subscriber count, and sorts the videos based on the rating value in descending order. Finally, it prints the title, subtitles presence, and best moments of each video in the sorted list.
print("Video Info:", get_video_info("PYskozIWh-E"))