from datetime import datetime, timedelta  # Add this import statement
from collections import defaultdict
import os
import csv
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import os.path
import google.auth.transport.requests
import google.oauth2.credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Load or create credentials from token file
def load_credentials():
    creds = None
    if os.path.exists('token.json'):
        creds = google.oauth2.credentials.Credentials.from_authorized_user_file('token.json')
    return creds

# Save credentials to token file
def save_credentials(credentials):
    token_path = 'token.json'
    with open(token_path, 'w') as token_file:
        token_file.write(credentials.to_json())

# Authenticate user
def authenticate():
    creds = load_credentials()
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file("c:\\GitHub\\bestQuest\\telegram_bot\\data_scraping\\client_secret.json", ['https://www.googleapis.com/auth/youtube.readonly'])
        creds = flow.run_local_server(port=0)
        save_credentials(creds)
    return googleapiclient.discovery.build('youtube', 'v3', credentials=creds)

# Fetch the latest 13 videos from a given channel
def get_latest_videos(youtube, channel_link):
    channel_id = channel_link.split("/channel/")[-1]
    request = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        maxResults=13,
        order="date",
        type="video"
    )
    response = request.execute()
    titles = [item["snippet"]["title"] for item in response["items"]]
    return titles

# Fetch the top 25 videos of the channel by number of views in the last two years
def get_top_videos(youtube, channel_link):
    channel_id = channel_link#.split("/channel/")[-1]
    request = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        maxResults=25,
        #q="keyword1 keyword2",
        #relatedToVideoId="VIDEO_ID",
        order="rating",
        publishedAfter=(datetime.now() - timedelta(days=730)).strftime('%Y-%m-%dT%H:%M:%SZ'),
        type="video"
    )
    #request = youtube.playlistItems().list(
    #     part="snippet",
    #     playlistId="PLAYLIST_ID",
    #     maxResults=25
    # )
    response = request.execute()
    videos = []
    #print(response["items"])
    for item in response["items"]:
        channel = item["snippet"]["channelTitle"]
        title = item["snippet"]["title"]
        video_id = item["id"]["videoId"]
        watch_count, like_count = get_video_stats(youtube, video_id)
        video_date = item["snippet"]["publishedAt"]
        guest_name = extract_guest_name(title)
        guest_channel_link = get_channel_link(youtube, guest_name)
        video_link = f"youtu.be/{video_id}"
        description = get_video_description(youtube, video_id)
        chapters = extract_chapters(description)
        transcript_request = youtube.captions().list(
            part="snippet",
            videoId=video_id
        )
        transcript = "subs"#transcript_request.execute()
        videos.append({
            "channel": channel,
            "title": title,
            "video_id": video_id,
            "watch_count": watch_count,
            "like_count": like_count,
            "video_date": video_date,
            "guest_name": guest_name,
            "guest_channel_link": guest_channel_link,
            "video_link": video_link,
            "chapters": chapters,
            "subs": transcript
        })
    # Sort videos by video_date
    videos.sort(key=lambda x: x["video_date"], reverse=True)
    return videos

# Extract guest name from title
def extract_guest_name(title):
    if "@" in title:
        start_index = title.find("@") + 1
        end_index = start_index
        while end_index < len(title) and title[end_index].isalnum():
            end_index += 1
        return title[start_index:end_index]
    return None

# Get video statistics (watch count, like count)
def get_video_stats(youtube, video_id):
    request = youtube.videos().list(
        part="statistics",
        id=video_id
    )
    response = request.execute()
    stats = response["items"][0]["statistics"]
    watch_count = stats.get("viewCount", 0)
    like_count = stats.get("likeCount", 0)
    return watch_count, like_count

# Get video description
def get_video_description(youtube, video_id):
    request = youtube.videos().list(
        part="snippet",
        id=video_id
    )
    response = request.execute()
    return response["items"][0]["snippet"].get("description", "")

# Extract lines starting with numbers from video descriptions
def extract_chapters(description):
    chapters = []
    for line in description.split("\n"):
        if line.strip().startswith(tuple(map(str, range(10)))) or (line.find(":") >= 0 and line.find("/") < 0):
            chapters.append(line.strip())
    return "\n".join(chapters)

# Get link to the guest's channel based on the guest name
def get_channel_link(youtube, guest_name):
    if guest_name:
        request = youtube.channels().list(
            part="snippet",
            forUsername=guest_name
        )
        response = request.execute()
        if "items" in response and response["items"]:
            return f"https://www.youtube.com/channel/{response['items'][0]['id']}"
    return None

# Save videos information to CSV table
def save_to_csv(videos, channel_id):
    csv_filename = f"{channel_id}_channel_videos.csv"
    with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
        #fieldnames = ["Channel","Title", "vidID", "Watch Count", "Like Count", "Video Date", "Guest Name", "Guest Channel Link", "vidurl", "Chapters"]#, "Most Replayed Moment Chapter"
        fieldnames = ["Title","Subheading","Slug","Member-Only","Featured","Publish Date","Reading Time","Image","Type","Author","Author X/Twitter URL","videoLink","Duration","Content","Pro Content"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for video in videos:
            writer.writerow({
                "Title": video["title"],
                "Subheading": video["channel"],
                "Slug": video["video_id"],
                "Member-Only":0,
                "Featured":0,
                "Publish Date": video["video_date"],
                "Reading Time": video["watch_count"],       
                "Image": "https://i.ytimg.com/vi/" + video["video_id"] + "/maxresdefault.jpg",
                "Type":"OriginalContent",
                "Author": video["guest_name"],
                "Author X/Twitter URL": video["guest_channel_link"],
                "videoLink": video["video_link"],
                "Duration":"4:20",
                "Content": video["chapters"].replace('\n', '<br>'),
                "Pro Content": video["subs"].replace('\n', '<br>')
                #"Most Replayed Moment Chapter": video["most_replayed_chapter"]
            })
    print(f"Top 25 videos information saved to {csv_filename}")

# Use YouTube API to get the most replayed timestamp
def get_most_replayed_timestamp(youtube, video_id):
    request = youtube.videos().list(
        part="statistics",
        id=video_id
    )
    response = request.execute()
    if "items" in response and response["items"]:
        video_stats = response["items"][0]["statistics"]
        if "mostPopularSection" in video_stats:
            most_replayed_timestamp = video_stats["mostPopularSection"]["time"]
            return most_replayed_timestamp
        else:
            print(response["items"][0]["statistics"])
    return None

# Find the chapter containing the most replayed timestamp
def find_chapter_for_timestamp(chapters, timestamp):
    bestChap = None
    for chapter in chapters.split("\n"):
        chapter_info = chapter.split(" ")
        if len(chapter_info) > 1:
            chapter_start_time = parse_chapter_time(chapter_info[0])
            if chapter_start_time <= timestamp:  # Allow a 10-second margin
                bestChap = chapter_start_time
    return bestChap

# Update videos dictionary with most replayed moment chapter
def update_videos_with_replayed_chapter(youtube, videos):
    for video in videos:
        most_replayed_timestamp = get_most_replayed_timestamp(youtube, video["video_id"])
        if most_replayed_timestamp is not None:
            most_replayed_chapter = find_chapter_for_timestamp(video["chapters"], most_replayed_timestamp)
            video["most_replayed_chapter"] = video["video_link"] + "?t=" + most_replayed_chapter
        else:
            video["most_replayed_chapter"] = "No data available"
    return videos

# Parse chapter time from string to seconds
def parse_chapter_time(chapter_time_str):
    parts = chapter_time_str.split(":")
    if len(parts) == 3:
        hours, minutes, seconds = map(int, parts)
        total_seconds = hours * 3600 + minutes * 60 + seconds
        return total_seconds
    elif len(parts) == 2:
        minutes, seconds = map(int, parts)
        total_seconds = minutes * 60 + seconds
        return total_seconds
    else:
        return int(parts[0])

#Here's an improved version of the script that includes the actual names of the channels in the result, sorts the statistics in descending order, and adds a congratulatory message for the top 3 winners:
def get_channel_name(youtube, channel_id):
    request = youtube.channels().list(
        part="snippet",
        id=channel_id
    )
    response = request.execute()
    return response["items"][0]["snippet"]["title"]

def get_videos_from_playlist(youtube, playlist_id):
    channel_ids = set()
    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=playlist_id,
        maxResults=50
    )
    while request:
        response = request.execute()
        for item in response["items"]:
            channel_ids.add(item["snippet"]["channelId"])
        request = youtube.playlistItems().list_next(request, response)
    return channel_ids

def aggregate_playlist_statistics(youtube, playlist_ids):
    channel_video_counts = defaultdict(int)
    for playlist_id in playlist_ids:
        channel_ids = get_videos_from_playlist(youtube, playlist_id)
        for channel_id in channel_ids:
            channel_video_counts[channel_id] += 1
    return channel_video_counts
    
# Main function
def main():
    youtube = authenticate()
    channel_link = input("Enter the link to the YouTube channel: ")
    channel_id = channel_link.split("/channel/")[-1]
    videos = get_top_videos(youtube, channel_link)
    #videos = update_videos_with_replayed_chapter(youtube, videos)
    save_to_csv(videos, channel_id)


    ##################
    ####################
    # playlist_ids = ["PLAYLIST_ID_1", "PLAYLIST_ID_2", "PLAYLIST_ID_3"]  # List of playlist IDs
    # statistics = aggregate_playlist_statistics(youtube, playlist_ids)

    # sorted_statistics = sorted(statistics.items(), key=lambda x: x[1], reverse=True)

    # for i, (channel_id, video_count) in enumerate(sorted_statistics):
    #     channel_name = get_channel_name(youtube, channel_id)
    #     print(f"{i+1}. Channel '{channel_name}' has {video_count} videos in the playlists.")

    # # Congratulatory message for the top 3 winners
    # top_3_winners = sorted_statistics[:3]
    # if top_3_winners:
    #     print("\nCongratulations to the top 3 winners:")
    #     for i, (channel_id, _) in enumerate(top_3_winners):
    #         channel_name = get_channel_name(youtube, channel_id)
    #         print(f"{i+1}. {channel_name}")
    
    ##################
    #############

if __name__ == "__main__":
    main()