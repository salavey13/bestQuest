import requests
import csv
import base64
import json
from datetime import datetime
from urllib.parse import urlparse, parse_qs

# Constants
YOUTUBE_API_URL = "https://www.youtube.com/youtubei/v1/get_transcript?key=AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8"

# Function to save data to CSV file
def save_to_csv(filename, data):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)
    print(f"Data saved to {filename} successfully!")

# Function to retrieve the html content of a webpage
def get_html(url):
    response = requests.get(url)
    return response.text

# Function to parse the videoId parameter from a YouTube video URL
def get_video_id(video_url):
    parsed_url = urlparse(video_url)
    video_id = parse_qs(parsed_url.query).get('v')
    if video_id:
        return video_id[0]

# Function to retrieve the best moments for a video
def best_moments(video_id):
    vidIdParam = "\n\v" + video_id
    base64_string = base64.b64encode(vidIdParam.encode("utf-8")).decode("utf-8")

    headers = {
        "Content-Type": "application/json",
    }

    body = json.dumps(
        {
            "context": {"client": {"clientName": "WEB", "clientVersion": "2.9999099"}},
            "params": base64_string,
        }
    )

    response = requests.post(YOUTUBE_API_URL, headers=headers, data=body)
    return response.text

# Function to convert timestamps to seconds
def convert_timestamp_to_seconds(timestamp):
    parts = timestamp.split(':')
    if len(parts) == 2:
        minutes = int(parts[0])
        seconds = int(parts[1])
        return minutes * 60 + seconds
    elif len(parts) == 3:
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = int(parts[2])
        return hours * 3600 + minutes * 60 + seconds
    else:
        raise ValueError("Invalid timestamp format. Please use either 'MM:SS' or 'HH:MM:SS'.")

# Function to convert seconds to timestamp
def convert_seconds_to_timestamp(seconds):
    hours = seconds // 3600
    minutes = ((seconds % 3600) // 60)
    seconds = seconds % 60
    if hours == 0:
        timestamp = f"{minutes:02d}:{seconds:02d}"
    else:
        timestamp = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return timestamp  



# Main function
def main():
    playlist_url = input("Enter the URL of the YouTube playlist: ")
    html_content = get_html(playlist_url)

    unique_video_ids = set()
    moments = []

    # Search for all unique videoId parameters in the playlist
    for link in html_content.split("{\"playlistVideoRenderer\":{\"videoId\":\""):
        video_id = link[0:11]
        if video_id:
            unique_video_ids.add(video_id)

    # Retrieve best moments for each video
    for video_id in unique_video_ids:
        video_moments = best_moments(video_id)
        if video_moments is not None:
            moments.extend(video_moments)

    # Sort moments by view count
    moments.sort(key=lambda x: x['viewCount'], reverse=True)

    # Save moments to CSV file
    filename = "moments.csv"
    data = [[moment['text'], moment['timestamp'], moment['viewCount']] for moment in moments]
    save_to_csv(filename, data)

if __name__ == "__main__":
    main()