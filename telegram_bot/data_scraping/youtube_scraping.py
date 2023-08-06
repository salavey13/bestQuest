from googleapiclient.discovery import build
import isodate
import datetime
import text_processing.text_helper
import re
import pandas as pd
# pip install pandas
from googleapiclient.errors import HttpError
from extractplaylisttocsv import create_service
import youtube_dl
import json
from pprint import pprint
import os
#### SIDE API ###
#curl -s 'https://www.youtube.com/youtubei/v1/get_transcript?key=AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8' -H 'Content-Type: application/json' --data-raw "{\"context\":{\"client\":{\"clientName\":\"WEB\",\"clientVersion\":\"2.9999099\"}},\"params\":\"$(printf '\n\x0bVIDEO_ID' | base64)\"}"

#subs:
#curl -s 'https://www.youtube.com/youtubei/v1/get_transcript?key=AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8' -H 'Content-Type: application/json' --data-raw "{\"context\":{\"client\":{\"clientName\":\"WEB\",\"clientVersion\":\"2.9999099\"}},\"params\":\"$(printf '\n\x0bSL-AowV25vI' | base64)\"}"

#info:
#https://yt.lemnoslife.com/noKey/videos?part=snippet&id= lgKbm7mIfg0

#best moment:
#https://yt.lemnoslife.com/videos?part=mostReplayed&id= lgKbm7mIfg0



def get_video_duration(video_id, api_key):
    youtube = build('youtube', 'v3', developerKey=api_key)

    # Call the API to retrieve the video details
    response = youtube.videos().list(
        part='contentDetails',
        id=video_id
    ).execute()

    # Extract the duration from the response
    duration = response['items'][0]['contentDetails']['duration']
    duration_seconds = isodate.parse_duration(duration).total_seconds()

    return duration_seconds

def convert_duration(duration):
	try:
		h = int(re.search('\d+H', duration)[0][:-1]) * 60**2  if re.search('\d+H', duration) else 0 # hour
		m = int(re.search('\d+M', duration)[0][:-1]) * 60  if re.search('\d+M', duration) else 0 # minute
		s = int(re.search('\d+S', duration)[0][:-1])  if re.search('\d+S', duration) else 0 # second
		return h + m + s
	except Exception as e:
		print(e)
		return 0

def retrieve_playlists(service, channel_id):
    playlists = []
    try:
        response = service.playlists().list(
            part='contentDetails,snippet,status',
            channelId=channel_id,
            maxResults=50
        ).execute()

        playlists.extend(response.get('items'))
        nextPageToken = response.get('nextPageToken')

        while nextPageToken:
            response = service.playlists().list(
                part='contentDetails,snippet,status',
                channelId=channel_id,
                maxResults=50,
                pageToken=nextPageToken
            ).execute()
            playlists.extend(response.get('items'))
            nextPageToken = response.get('nextPageToken')
        return playlists
    except HttpError as e:
        errMsg = json.loads(e.content)
        print('HTTP Error:')
        print(errMsg['error']['message'])
        return []

def retrieve_playlist_items(service, playlist_id):
    playlist_items = []
    try:
        response = service.playlistItems().list(
            part='contentDetails',
            playlistId=playlist_id,
            maxResults=50
        ).execute()

        playlist_items.extend(response['items'])
        nextPageToken = response.get('nextPageToken')

        while nextPageToken:
            response = service.playlistItems().list(
                part='contentDetails',
                playlistId=playlist_id,
                maxResults=50,
                pageToken=nextPageToken
            ).execute()

            playlist_items.extend(response['items'])
            nextPageToken = response.get('nextPageToken')
            print('Token {0}'.format(nextPageToken))
        return playlist_items
    except HttpError as e:
        errMsg = json.loads(e.content)
        print('HTTP Error:')
        print(errMsg['error']['message'])
        return []
    except Exception as e:
        errMsg = json.loads(e.content)
        print('Error:')
        print(errMsg['error']['message'])
        return []

def extract_video_info(url):
    ydl_opts = {
        'ignoreerrors': True,
        'skip_download': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['en'],
        'skip_playlist': False,
        'extract_flat': True,
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            result = ydl.extract_info(url, download=False)
            return result
        except youtube_dl.utils.DownloadError as e:
            print(f'Error: {e}')

def extract_channel_subscribers(channel_id):
    try:
        youtube_api_service_name = "youtube"
        youtube_api_version = "v3"
        from googleapiclient.discovery import build
        youtube = build(youtube_api_service_name, youtube_api_version, cache_discovery=False)

        channel_request = youtube.channels().list(
            part="statistics",
            id=channel_id
        )
        channel_response = channel_request.execute()

        if 'items' in channel_response:
            subscribers = int(channel_response['items'][0]['statistics']['subscriberCount'])
            return subscribers
    
    except Exception as e:
        print(f'Error: {e}')
    
    return 0

def extract_playlist_videos(playlist_url):
    playlist_videos = {}
    channel_counts = {}
    playlist_id = re.search(r'list=(.*)', playlist_url).group(1)
    next_page_token = None
    
    while True:
        try:
            youtube_api_service_name = "youtube"
            youtube_api_version = "v3"
            from googleapiclient.discovery import build
            youtube = build(youtube_api_service_name, youtube_api_version, cache_discovery=False)
        
            playlist_request = youtube.playlistItems().list(
                part="snippet",
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token
            )
            playlist_response = playlist_request.execute()
        
            for item in playlist_response['items']:
                video_id = item['snippet']['resourceId']['videoId']
                video_url = f'https://www.youtube.com/watch?v={video_id}'
                video_info = extract_video_info(video_url)
                if video_info and 'subtitles' in video_info:
                    subtitle_status = "Subtitles present"
                else:
                    subtitle_status = "No subtitles"
                
                description = item['snippet']['description']
                if re.search(r'Chapters:', description, re.IGNORECASE):
                    chapter_status = "Chapters defined"
                else:
                    chapter_status = "No chapters"
                
                # Extract channel links from title and description
                channel_links = []
                if video_info and 'title' in video_info:
                    title = video_info['title']
                    if '@' in title:
                        channel_links += re.findall(r'(@[^\s]+)', title)
                
                if '@' in description:
                    channel_links += re.findall(r'(@[^\s]+)', description)
                
                # Track channel link counts
                for link in channel_links:
                    channel_counts[link] = channel_counts.get(link, 0) + 1
                
                playlist_videos[video_id] = {
                    'title': title,
                    'description': description,
                    'subtitle_status': subtitle_status,
                    'chapter_status': chapter_status,
                    'channel_links': channel_links
                }
                
            next_page_token = playlist_response.get('nextPageToken')
            if not next_page_token:
                break

        except Exception as e:
            print(f'Error: {e}')
            break
    
    # Save final channel link counts along with channel information
    for link, count in channel_counts.items():
        if link not in playlist_videos:
            playlist_videos[link] = {}
        
        channel_id = link.lstrip('@')
        subscribers = extract_channel_subscribers(channel_id)
        playlist_videos[link]['link_count'] = count
        playlist_videos[link]['subscribers'] = subscribers
    
    return playlist_videos

def calculate_video_rating(video_info, max_video_views, max_channel_subs, weight_video_views, weight_link_subs, weight_channel_subs):
    video_views = video_info['view_count']
    guest_subs = sum(item['subscribers'] for item in video_info['channel_links'])
    channel_subs = video_info.get('subscribers', 0)
    
    rating = ((video_views / max_video_views) * weight_video_views +
              (guest_subs / max_channel_subs) * weight_link_subs +
              (channel_subs / max_channel_subs) * weight_channel_subs) / \
             (weight_video_views + weight_link_subs + weight_channel_subs)
    
    return rating

def extract_channels_by_topic(topic, num):
    # Set up your YouTube_Data_API credentials
    api_key = os.environ["YouTube_Data_API"]

    # Create a YouTube API client
    youtube = build('youtube', 'v3', developerKey=api_key)

    # Retrieve the top 420 YouTubers covering the Ukraine conflict
    top_channels = youtube.search().list(q=topic, type='channel', part='snippet', maxResults=num).execute()

    # Extract the channel IDs from the search results
    channel_ids = [item['id']['channelId'] for item in top_channels['items']]

    # Create a CSV file to save the extracted data
    csv_file = open('top_youtube_channels.csv', 'w', newline='', encoding='utf-8')
    csv_writer = csv.writer(csv_file)

    # Write the header row to the CSV file
    csv_writer.writerow(['Channel ID', 'Channel Title', 'Description'])

    # Retrieve and save the channel information
    for channel_id in channel_ids:
        channel_info = youtube.channels().list(part='snippet',id=channel_id).execute()
        channel_title = channel_info['items'][0]['snippet']['title']
        channel_description = channel_info['items'][0]['snippet']['description']
        csv_writer.writerow([channel_id, channel_title, channel_description])
        print(channel_title)

    # Close the CSV file
    csv_file.close()

def main(channel_id):
    CLIENT_SECRET_FILE = 'client-secret.json'
    API_NAME = 'youtube'
    API_VERSION = 'v3'
    SCOPES = ['https://www.googleapis.com/auth/youtube']

    service = create_service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
    playlists = retrieve_playlists(service, channel_id)

    if not playlists:
        print('No pliaylist found.')
        return

    excelWriter = pd.ExcelWriter('Playlists for Channel Id {0} {1}.xlsx'.format(channel_id, datetime.datetime.now().strftime('%Y_%m_%d %H_%M_%S')))

    for playlist in playlists:
        playlist_id = playlist['id']
        playlist_title = playlist['snippet']['title']

        playlist_items = retrieve_playlist_items(service, playlist_id)

        videos = tuple(v['contentDetails'] for v in playlist_items)

        videos_info = []
        for batch_num in range(0, len(videos), 50):
            video_batch = videos[batch_num: batch_num+50]

            response_videos = service.videos().list(
                id=','.join(list(map(lambda v: v['videoId'], video_batch))),
                part='snippet,contentDetails,statistics',
                maxResults=50
            ).execute()

            videos_info.extend(response_videos['items'])

        if videos_info:
            rows = []
            columns = ['Video Id', 'Video Title', 'Description', 'Duration (s)', 'Licensed Content', 'Published', 'Tags',
                                'Thumbnail Url', 'View Count', 'Like Count', 'Dislike Count', 'Comment Count', 'Video Url']

            for video in videos_info:
                rows.append(
                    [
                        video['id'],
                        video['snippet']['title'],
                        video['snippet']['description'],
                        convert_duration(video['contentDetails']['duration']),
                        video['contentDetails']['licensedContent'],
                        video['snippet']['publishedAt'][:-1],
                        ', '.join(video['snippet']['tags']) if video['snippet'].get('tags') else '',
                        video['snippet']['thumbnails']['default']['url'],
                        int(video['statistics']['viewCount']) if video['statistics'].get('viewCount') else 0,
                        video['statistics']['likeCount'] if video['statistics'].get('likeCount') else 0,
                        video['statistics']['dislikeCount'] if video['statistics'].get('dislikeCount') else 0,
                        video['statistics']['commentCount'] if video['statistics'].get('commentCount') else 0,
                        'https://www.youtube.com/watch?v={0}'.format(video['id'])
                    ]
                )

            df = pd.DataFrame(data=rows, columns=columns)
            sheet_title = playlist_title.replace(':', '').replace('/', '').replace('\\', '').replace('?', '')[:30]
            df.to_excel(excelWriter, sheet_name=sheet_title, index=False)

    excelWriter.save()
    print('Channel playlist report exported.')

def search_keywords_in_subtitles(video, keywords):
    # Get all subtitles as text
    all_subtitles_text = get_all_subtitles_as_text(video)

    # Extract the most mentioned nouns from the subtitles
    top_nouns = text_processing.text_helper.extract_top_13_nouns(all_subtitles_text, 69)

    # Filter the input keywords based on the top nouns
    filtered_keywords = [keyword for keyword in keywords if keyword in top_nouns]
    
    keyword_table = []
    for subtitle in video.subtitles:
        for keyword in filtered_keywords:
            if keyword in subtitle.text:
                # Calculate the rating based on proximity to "button" and other factors
                rating = calculate_rating(subtitle, keyword)

                # Append the rating along with the keyword and timestamp
                keyword_table.append((keyword, subtitle.start_timestamp, rating))
    
    # Sort the keyword table based on rating in descending order
    keyword_table.sort(key=lambda x: x[2], reverse=True)
    
    # Return the updated table
    return keyword_table

def search_keywords_in_playlist(playlist, keywords):
    all_results = []

    for video in playlist.videos:
        # Execute search on each video in the playlist
        video_results = search_keywords_in_subtitles(video, keywords)
        all_results.extend(video_results)

    return all_results

def calculate_rating(subtitle, keyword):
    rating = 0
    
    # Check if proximity words like "button", "click", or "menu" are present in the subtitle
    proximity_words = ["button", "click", "menu", "option", "select", "tool", "interface"]
    presence_of_proximity_words = any(word in subtitle.text.lower() for word in proximity_words)

    if presence_of_proximity_words:
        rating += 1  # Increase the rating if proximity words are present
    
    # TODO Add additional logic or factors to calculate the rating based on other criteria
    #~calculate_video_rating
    return rating

if __name__ == '__main__' :
    # Example usage

    channel_id = 'UCW5gUZ7lKGrAbLOkHv2xfbw'
    main(channel_id)

    duration = get_video_duration(video_id, api_key)
    print(duration)
    
    
    playlist_link = "https://www.youtube.com/playlist?list=PL-osiE80TeTt2d9bfVyTiXJA-UTHn6WwU"
    video_weight_views = 0.5
    link_weight_subs = 0.3
    channel_weight_subs = 0.2

    playlist_videos = extract_playlist_videos(playlist_link)
    max_video_views = max(video_info['view_count'] for video_info in playlist_videos.values())
    max_channel_subs = max(video_info.get('subscribers', 0) for video_info in playlist_videos.values() if 'subscribers' in video_info)

    for item_id, video_info in playlist_videos.items():
        if item_id.startswith("http"):
            print(f"Channel Link: {item_id}")
            print(f"Link Count: {video_info.get('link_count', 0)}")
            print(f"Subscribers: {video_info.get('subscribers', 0)}")
            print("---")
        else:
            video_id = item_id
            print(f"Video ID: {video_id}")
            print(f"Title: {video_info['title']}")
            print(f"Description: {video_info['description']}")
            print(f"Subtitle Status: {video_info['subtitle_status']}")
            print(f"Chapter Status: {video_info['chapter_status']}")
            print(f"Channel Links: {', '.join(video_info['channel_links'])}")
            print(f"Rating: {calculate_video_rating(video_info, max_video_views, max_channel_subs, video_weight_views, link_weight_subs, channel_weight_subs)}")
            print("---")