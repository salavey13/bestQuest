from datetime import datetime, timedelta  # Add this import statement
from collections import defaultdict
import os
import csv
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re
import os.path
import google.auth.transport.requests
import google.oauth2.credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import subprocess
from bs4 import BeautifulSoup #python -m pip install bs4
import pandas as pd
import gspread #python -m pip install gspread
from gspread_dataframe import set_with_dataframe #python -m pip install gspread_dataframe oauth2client.service_account
from oauth2client.service_account import ServiceAccountCredentials
import argparse

# Your existing script logic here that processes the channel ID and saves data to CSV

#print(f'Processing data for Channel ID: {channel_id} and saving to {output_csv}.')
# Function to upload CSV file to Google Docs and make it publicly accessible
def upload_to_google_docs(csv_file_path):
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']

    credentials = ServiceAccountCredentials.from_json_keyfile_name("c:\\GitHub\\bestQuest\\telegram_bot\\data_scraping\\client_secret.json", scope)
    gc = gspread.authorize(credentials)

    # Open the Google Spreadsheet
    sh = gc.open('Top13')

    # Create a new worksheet
    worksheet = sh.add_worksheet(title='New Worksheet', rows="100", cols="20")

    # Upload CSV data to the worksheet
    df = pd.read_csv(csv_file_path)
    set_with_dataframe(worksheet, df)

    # Share the spreadsheet publicly for download
    sh.share('', perm_type='anyone', role='reader')

    # Get the shareable download link of the uploaded file
    sheet_id = sh.id
    sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

    return sheet_url

# Concatenate CSV files into a mega CSV table
def concatenate_csv_files(csv_files):
    df_list = []

    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        df['file'] = upload_to_google_docs(csv_file)  # Add a new column with the Google Docs link
        df_list.append(df)

    mega_df = pd.concat(df_list, ignore_index=True)

    # Write the mega CSV table to a file
    mega_df.to_csv('mega_csv_table.csv', index=False)

# # List of CSV files to process
# csv_files = ['csv_file1.csv', 'csv_file2.csv', 'csv_file3.csv']

# # Call the function to concatenate CSV files and create the mega CSV table
# concatenate_csv_files(csv_files)
# 
    
NUMBER=13

# Save videos information to CSV table
def save_to_csv(videos, channel_id):
    csv_filename = f"{channel_id}_channel_videos.csv"
    with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
        #fieldnames = ["Channel","Title", "vidID", "Watch Count", "Like Count", "Video Date", "Guest Name", "Guest Channel Link", "vidurl", "Chapters"]#, "Most Replayed Moment Chapter"
        fieldnames = ["Title","Subheading","Slug","Member-Only","Featured","Publish Date","Views/Subs","Image","Type","Author","Author X/Twitter URL","videoLink","Duration","Content","Pro Content"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for video in videos:
            chapter_list_best_chapter = ""
            try:
                # Call the separate script and capture its output and errors
                process = subprocess.Popen(['python', 'telegram_bot\\data_scraping\\subtle_rEvolution.py', video["video_id"]], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output, errors = process.communicate()

                if errors:
                    print("An error occurred while executing the separate script:")
                    print(errors.decode('utf-8'))
                else:
                    # Save the output text into variables
                    chapter_list_best_chapter = output.decode('utf-8')#.splitlines()  # Assuming output contains chapter list and best chapter

                    #print("Chapter List:")
                    #print(chapter_list_best_chapter)




            except subprocess.CalledProcessError as e:
                print("CalledProcessError: Unable to execute the separate script.")
            except Exception as e:
                print("An unexpected error occurred:", e)


            writer.writerow({
                "Title": video["title"],
                "Subheading": video["channel"],#channelName
                "Slug": video["video_id"],#@channel
                "Member-Only":0,
                "Featured":0,
                "Publish Date": video["video_date"],
                "Views/Subs": video["watch_count"],       
                "Image": "https://i.ytimg.com/vi/" + video["video_id"] + "/maxresdefault.jpg",
                "Type": video["type"],#"OriginalContent",#or ContentMaker
                "Author": video["guest_name"],
                "Author X/Twitter URL": video["guest_channel_link"],
                #"Author TG URL": video["guest_channel_link"],
                #"Author Insta URL": video["guest_channel_link"],
                #"Author Patrein URL": video["guest_channel_link"],
                "videoLink": "https://www.youtube.com/watch?v=" + video["video_id"],
                "Duration":"4:20",
                "Content": beautify_html(chapter_list_best_chapter.replace('\n', '<br>')),
                "Pro Content": '<br>' + video["chapters"].replace('\n', '<br>')
                #"Most Replayed Moment Chapter": video["most_replayed_chapter"]
                #Comment1
                #CommentAuthor1
                #Comment2
                #CommentAuthor2
                #Comment3
                #CommentAuthor3
                #PrimaryColor
                #PrimaryBackground
                #SecondaryColor
                #SecondaryBackground
                #TextColor
            })
    print(f"Top {NUMBER} videos information saved to {csv_filename}")


def get_channel_ids_from_playlist(playlist_id, api_key):
    base_url = 'https://www.googleapis.com/youtube/v3/playlistItems'
    
    params = {
        'part': 'snippet',
        'playlistId': playlist_id,
        'maxResults': 50,  # Maximum results per call
        'key': api_key
    }

    channel_ids = []

    # Retrieve playlist items using pagination
    next_page_token = None
    while True:
        if next_page_token:
            params['pageToken'] = next_page_token
        
        response = requests.get(base_url, params=params)
        data = response.json()
        
        for item in data['items']:
            channel_id = item['snippet']['channelId']
            channel_ids.append(channel_id)
        
        next_page_token = data.get('nextPageToken')

        if not next_page_token:
            break

    return channel_ids

# Example usage
# playlist_id = 'YOUR_PLAYLIST_ID_HERE'
# api_key = 'YOUR_YOUTUBE_API_KEY_HERE'
# channel_ids = get_channel_ids_from_playlist(playlist_id, api_key)
# print(channel_ids)

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
    watch_count = int(stats.get("viewCount", 0))
    like_count = int(stats.get("likeCount", 0))
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
def get_videos_from_playlist(youtube, playlist_id):
    video_channel_ids = []
    next_page_token = None
    while True:
        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()
        for item in response.get("items", []):
            try:
                video_channel_ids.append(item["snippet"]["videoOwnerChannelId"])
            except KeyError:
                print(f"Error: 'videoOwnerChannelId' key not found for item: {item}")
        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break
    return video_channel_ids

def aggregate_playlist_statistics(youtube, playlist_ids):
    channel_video_counts = defaultdict(int)
    for playlist_id in playlist_ids:
        video_channel_ids = get_videos_from_playlist(youtube, playlist_id)
        for channel_id in video_channel_ids:
            channel_video_counts[channel_id] += 1
    return channel_video_counts

def get_top_video_from_channel(youtube, channel_id):
    request = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        maxResults=1,
        order="viewCount",
        publishedAfter="2022-01-01T00:00:00Z",
        type="video"
    )
    response = request.execute()
    if response["items"]:
        top_video = response["items"][0]
        return {
            "Title": top_video["snippet"]["title"],
            "Channel": top_video["snippet"]["channelTitle"],
            "Published Date": top_video["snippet"]["publishedAt"],
            "Video Link": f"https://www.youtube.com/watch?v={top_video['id']['videoId']}"
        }
    else:
        return None





    # Main function


def beautify_html(input_html):
    # Parse the input HTML string
    soup = BeautifulSoup(input_html, 'html.parser')
    body_content = []

    # Iterate through each line of the input HTML
    for line in soup.stripped_strings:
        # Wrap the first word in <b> tag if it ends with ":"
        words = line.split()
        if words:
            if words[0].endswith(":"):
                words[0] = f"<br><pre><b>{words[0]}</b>"

            if len(words) > 1 and (words[1].startswith("http:") or words[1].startswith("https:")):
                words[1] = f"<br><pre><b><a href='{words[1]}'>{words[1]}</a></b><br>"

            line = ' '.join(words)

        # Wrap lines like "Video Description" in <h2> and "Official Chapters:" in <h3>
        if line.strip().startswith("<br><pre><b>OfficialChapters") or line.strip().startswith("### Best Moments"):
            body_content.append(f"<pre><pre><h5>{line}</h5>")
        else:
            body_content.append(line)

    # Wrap links in <a href=...> tag
    for i, word in enumerate(body_content):
        if re.match(r'https?://', word):
            body_content[i] = f"<a href='{word}'>{word}</a>"

    # Replace <br> tags with newline characters
    for br in soup.find_all('br'):
        br.replace_with('\n')

    # Wrap each line with <br> tag
    body_content = [f"{line}<br>" for line in body_content]

    # Return the beautified body content as HTML
    return ''.join(body_content)




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

# Extract the video ID of the channel trailer
def get_channel_trailer(youtube, channel_id):
    # Retrieve the content details of the channel
    channel_request = youtube.channels().list(
        part='contentDetails',
        id=channel_id
    )
    channel_response = channel_request.execute()

    uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    # Retrieve the videos in the uploads playlist
    playlist_request = youtube.playlistItems().list(
        part='snippet',
        playlistId=uploads_playlist_id,
        maxResults=1  # Fetch only the first video
    )
    playlist_response = playlist_request.execute()

    # Extract the video ID of the channel trailer
    channel_trailer_video_id = playlist_response['items'][0]['snippet']['resourceId']['videoId']

    return channel_trailer_video_id

# Fetch the top 25 videos of the channel by number of views in the last two years
def get_top_videos(youtube, channel_id):
    print(channel_id)
     # Request to fetch channel information
    channel_info_request = youtube.channels().list(
        part='snippet,contentDetails,statistics',
        id=channel_id
    )
    channel_info_response = channel_info_request.execute()
    print(channel_info_response)
    # Extract relevant data from the response
    channel_name = channel_info_response['items'][0]['snippet']['title']
    custom_url = channel_info_response['items'][0]['snippet'].get('customUrl', '')
    channel_description = channel_info_response['items'][0]['snippet']['description']
    subscriber_count = channel_info_response['items'][0]['statistics'].get('subscriberCount', 0)
    # Extract the video ID of the channel trailer
    channel_trailer_video_id = get_channel_trailer(youtube, channel_id)
    
    #1111111111111111 from channelarestest
    # request = youtube.search().list(
    #     part="snippet",
    #     channelId=channel_id,
    #     maxResults=NUMBER,
    #     q="латынина",
    #     #relatedToVideoId="5P5kKgDZV1A",
    #     order="rating",
    #     publishedAfter=(datetime.now() - timedelta(days=730)).strftime('%Y-%m-%dT%H:%M:%SZ'),
    #     type="video"
    # )

    #2222222222222222 FROM PLAYLIST
    #request = youtube.playlistItems().list(
    #     part="snippet",
    #     playlistId="PLAYLIST_ID",
    #     maxResults=25
    # )

    #33333333333333333 PARTICULAR VIDEO
    # request = youtube.videos().list(
    #     part="snippet",
    #     id="5P5kKgDZV1A"
    # )



    # top_videos_request = youtube.search().list(
    #     part='snippet',
    #     channelId=channel_id,
    #     maxResults=13,
    #     order='viewCount',  # You can change the order based on metrics
    #     type='video',
    #     publishedAfter='2022-02-01T00:00:00Z'  # Videos since February 2022
    # )


    # Make request to get 50 most popular videos sorted by viewCount
    videos_most_popular_request = youtube.search().list(
        part='snippet',
        channelId=channel_id,
        type='video',
        order='viewCount',
        publishedAfter='2022-02-01T00:00:00Z',  # Videos since February 2022
        maxResults=50
    )
    videos_most_popular_response = videos_most_popular_request.execute()
    
    # Make request to get 50 newest videos sorted by publish date
    videos_newest_request = youtube.search().list(
        part='snippet',
        channelId=channel_id,
        type='video',
        maxResults=50,
        order='date'
    )
    videos_newest_response = videos_newest_request.execute()
    
    # Calculate ratio for most popular videos
    videos_most_popular = []
    for video_item in videos_most_popular_response['items']:
        view_count,like_count = get_video_stats(youtube, video_item["id"]["videoId"])

        ratio = like_count / view_count # if view_count > 0 else 0

        channel = video_item["snippet"]["channelTitle"]
        title = video_item["snippet"]["title"]
        video_id = video_item["id"]["videoId"]
        #video_id = "5P5kKgDZV1A"
        watch_count, like_count = get_video_stats(youtube, video_id)
        video_date = video_item["snippet"]["publishedAt"]
        guest_name = extract_guest_name(title)
        guest_channel_link = get_channel_link(youtube, guest_name)
        video_link = f"https://youtube.com/watch?v={video_id}"
        description = get_video_description(youtube, video_id)
        chapters = extract_chapters(description)
        # transcript_request = youtube.captions().list(
        #     part="snippet",
        #     videoId=video_id
        # )
        transcript = "subs"#transcript_request.execute()
        videos_most_popular.append({
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
            "subs": transcript,
            "type": "OriginalContent",
            'ratio': ratio
        })
    
        #videos_most_popular.append({'video_id': video_item['id'], 'ratio': ratio})
    
    # Calculate ratio for newest videos
    videos_newest = []
    for video_item in videos_newest_response['items']:
        video_id = video_item['id']['videoId']
        # view_count = int(video_item['statistics']['viewCount'])
        # like_count = int(video_item['statistics']['likeCount'])
        view_count,like_count = get_video_stats(youtube, video_id)
        ratio = like_count / view_count if view_count > 0 else 0

        channel = video_item["snippet"]["channelTitle"]
        title = video_item["snippet"]["title"]
        video_id = video_item["id"]["videoId"]
        #video_id = "5P5kKgDZV1A"
        watch_count, like_count = get_video_stats(youtube, video_id)
        video_date = video_item["snippet"]["publishedAt"]
        guest_name = extract_guest_name(title)
        guest_channel_link = get_channel_link(youtube, guest_name)
        video_link = f"https://youtube.com/watch?v={video_id}"
        description = get_video_description(youtube, video_id)
        chapters = extract_chapters(description)
        # transcript_request = youtube.captions().list(
        #     part="snippet",
        #     videoId=video_id
        # )
        transcript = "subs"#transcript_request.execute()
        videos_most_popular.append({
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
            "subs": transcript,
            "type": "OriginalContent",
            'ratio': ratio
        })

        #videos_newest.append({'video_id': video_id, 'ratio': ratio})

    # Combine both sets of videos and sort by ratio
    combined_videos = videos_most_popular + videos_newest
    sorted_combined_videos = sorted(combined_videos, key=lambda x: x['ratio'], reverse=True)

    top_videos = sorted_combined_videos[:NUMBER]
    top_videos.append({ #append channel info as first video with type "cannelInfo)"
            "channel": channel,
            "title": channel_name,
            "video_id": custom_url,
            "watch_count": subscriber_count,
            # "like_count": like_count,
            "video_date": '2022-02-01T00:00:00Z',
            "guest_name": "",
            "guest_channel_link": "",
            "video_link": "https://youtube.com/watch?v=" + channel_trailer_video_id,
            "chapters": channel_description,
            #TG
            #Insta
            #PatreonUrl
            "subs":"",# transcript,
            "type": "ContentMaker"
        })
    
    return top_videos
    #response = request.execute()
    #print(response["items"])
    # videos = []
    # videos.append({ #append channel info as first video with type "cannelInfo)"
    #         "channel": channel,
    #         "title": channel_name,
    #         "video_id": custom_url,
    #         "watch_count": subscriber_count,
    #         # "like_count": like_count,
    #         # "video_date": video_date,
    #         # "guest_name": guest_name,
    #         # "guest_channel_link": guest_channel_link,
    #         "video_link": "https://youtube.com/watch?v=" + channel_trailer_video_id,
    #         "chapters": channel_description,
    #         #TG
    #         #Insta
    #         #PatreonUrl
    #         #"subs": transcript,
    #         "type": "channelInfo"
    #     })
    
    # for item in response["items"]:
    #     channel = item["snippet"]["channelTitle"]
    #     title = item["snippet"]["title"]
    #     video_id = item["id"]["videoId"]
    #     #video_id = "5P5kKgDZV1A"
    #     watch_count, like_count = get_video_stats(youtube, video_id)
    #     video_date = item["snippet"]["publishedAt"]
    #     guest_name = extract_guest_name(title)
    #     guest_channel_link = get_channel_link(youtube, guest_name)
    #     video_link = f"https://youtube.com/watch?v={video_id}"
    #     description = get_video_description(youtube, video_id)
    #     chapters = extract_chapters(description)
    #     # transcript_request = youtube.captions().list(
    #     #     part="snippet",
    #     #     videoId=video_id
    #     # )
    #     transcript = "subs"#transcript_request.execute()
    #     videos.append({
    #         "channel": channel,
    #         "title": title,
    #         "video_id": video_id,
    #         "watch_count": watch_count,
    #         "like_count": like_count,
    #         "video_date": video_date,
    #         "guest_name": guest_name,
    #         "guest_channel_link": guest_channel_link,
    #         "video_link": video_link,
    #         "chapters": chapters,
    #         "subs": transcript,
    #         "type": "video"
    #     })
    # # Sort videos by video_date
    # videos.sort(key=lambda x: x["video_date"], reverse=True)
    #return videos



def main():
    parser = argparse.ArgumentParser(description='Process YouTube channel data')
    parser.add_argument('--channel_id', type=str, help='Channel ID to process')
    parser.add_argument('--output_csv', type=str, help='Name of the output CSV file')

    args = parser.parse_args()

    channel_id = args.channel_id
    output_csv = args.output_csv

    youtube = authenticate()
    # # List of CSV files to process
    # csv_files = ['csv_file1.csv', 'csv_file2.csv', 'csv_file3.csv']
    csv_files = []

    ##################
    ####################
    playlist_ids = ["PLDq9dRwju0A0n_fV51Fy48ZvA6mqdlgx1"]#, "PLAYLIST_ID_2", "PLAYLIST_ID_3"]  # List of playlist IDs
    statistics = aggregate_playlist_statistics(youtube, playlist_ids)

    sorted_statistics = sorted(statistics.items(), key=lambda x: x[1], reverse=True)

    for i, channel_id in enumerate(sorted_statistics[:5]):
        videos = get_top_videos(youtube, channel_id[0])
    
        if output_csv=="":
            
            print("1 OK" + channel_id[0] + "_" + videos[0]["channel"])
            save_to_csv(videos, channel_id[0] + "_" + videos[0]["channel"])
            csv_files.append(channel_id[0] + "_" + videos[0]["channel"] + "_channel_videos.csv")
        else:
            print("2 OK" + channel_id[0] + "_" + videos[0]["channel"])
            save_to_csv(videos, channel_id[0] + "_" + videos[0]["channel"])
            csv_files.append(output_csv)
    #     request = youtube.channels().list(
    #         part="snippet",
    #         id=channel_id
    #     )
    #     response = request.execute()
    #     channel_name = response["items"][0]["snippet"]["title"]
    #     print(f"{i+1}. Channel '{channel_name}' has {video_count} videos in the playlists.")

    # # Congratulatory message for the top 3 winners
    # top_3_winners = sorted_statistics[:3]
    # if top_3_winners:
    #     print("\nCongratulations to the top 3 winners:")
    #     for i, (channel_id, _) in enumerate(top_3_winners):
    #         request = youtube.channels().list(
    #             part="snippet",
    #             id=channel_id
    #         )
    #         response = request.execute()
    #         channel_name = response["items"][0]["snippet"]["title"]
    #         print(f"{i+1}. {channel_name}")
    #         top_video = get_top_video_from_channel(youtube, channel_id)
    #         if top_video:
    #             print(f"\nTop 1 video from top channel {i}:")
    #             for key, value in top_video.items():
    #                 print(f"{key}: {value}")
    #         else:
    #             print(f"\nNo videos found for top channel {i}")
    
    ##################
    #############
                                                                                                            # if channel_id=="":
                                                                                                            #     channel_link = input("Enter the link to the YouTube channel: ")
                                                                                                            #     channel_id = channel_link.split("/channel/")[-1]

                                                                                                            # videos = get_top_videos(youtube, channel_id)
                                                                                                            
                                                                                                            # if output_csv=="":
                                                                                                            #     save_to_csv(videos, channel_id)
                                                                                                            #     csv_files.append(f"{channel_id}_channel_videos.csv")
                                                                                                            # else:
                                                                                                            #     save_to_csv(videos, output_csv)
                                                                                                            #     csv_files.append(output_csv)

    
    # # Call the function to concatenate CSV files and create the mega CSV table
    concatenate_csv_files(csv_files)


if __name__ == "__main__":
    main()