import requests
#from bs4 import BeautifulSoup
import csv
import requests
import base64
import json
from datetime import datetime
import sys
from urllib.parse import urlparse, parse_qs


# Function to save data to CSV file
def save_to_csv(filename, data):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)
    print(f"Data saved to {filename} successfully!")

# Create example data
youtube_channels = [
    ['channel_id', 'channel_name', 'channel_description', 'channel_link'],
    [1, 'Channel 1', 'Description 1', 'https://www.youtube.com/channel1'],
    [2, 'Channel 2', 'Description 2', 'https://www.youtube.com/channel2'],
]

videos = [
    ['video_id', 'channel_id', 'host_id', 'guest_id', 'video_title', 'video_description', 'video_duration', 'video_link'],
    [1, 1, 1, 2, 'Video 1', 'Description 1', '10:30', 'https://www.youtube.com/video1'],
    [2, 2, 2, 1, 'Video 2', 'Description 2', '15:45', 'https://www.youtube.com/video2'],
]

articles = [
    ['article_id', 'chapter_id', 'article_type', 'article_name', 'article_info', 'article_conclusion', 'article_image_url', 'article_image_base64', 'article_video_url', 'article_embed_code'],
    [1, 1, 'picture', 'Article 1', 'Info 1', 'Conclusion 1', 'https://www.example.com/image1.jpg', '', '', ''],
    [2, 2, 'video', 'Article 2', 'Info 2', 'Conclusion 2', '', '', 'https://www.example.com/video2.mp4', '<iframe src="https://www.example.com/embed2"></iframe>'],
]

    # chapters = [
        # ['chapter_id', 'video_id', 'chapter_start_time', 'chapter_end_time', 'chapter_label', 'chapter_coolness_rating'],
        # [1, 1, '00:00:00', '00:05:30', 'Chapter 1', 0.8],
        # [2, 1, '00:05:31', '00:10:15', 'Chapter 2', 0.9],
    # ]

subtitles_scv = [
    ['subtitle_id', 'video_id', 'subtitle_start_time', 'subtitle_end_time', 'subtitle_text', 'chapter_coolness_rating'],
    [1, 1, '00:00:01', '00:00:05', 'Subtitle 1', 0.8],
    [2, 1, '00:00:06', '00:00:10', 'Subtitle 2', 0.9],
]

# Save data to CSV files
# save_to_csv('youtube_channels.csv', youtube_channels)
# save_to_csv('videos.csv', videos)
# save_to_csv('articles.csv', articles)
# save_to_csv('chapters.csv', chapters)
# save_to_csv('subtitles.csv', subtitles_scv)

# extract sub duration
def extract_sub_duration(json_data):
    # Parse the JSON data
    data = json.loads(json_data)
    last_timestamp = 0
    # Extract the subtitle cues
    try:
        cue_groups = data['actions'][0]['updateEngagementPanelAction']['content']['transcriptRenderer']['body']['transcriptBodyRenderer']['cueGroups']
        
        last_timestamp = convert_timestamp_to_seconds(cue_groups[len(cue_groups) - 1]['transcriptCueGroupRenderer']['formattedStartOffset']['simpleText'])
    except:
        last_timestamp = 3600000
     #   sys.exit("FUCK NO SUBS(")
        
#    print("LOLOLO",cue_groups[len(cue_groups) - 1]['transcriptCueGroupRenderer']['formattedStartOffset']['simpleText'])
    return last_timestamp

def extract_best_chapter(json_data, timestamp):
    # Parse the JSON data
    data = json.loads(json_data)
    video_description = data["items"][0]["snippet"]['description']
    lines = video_description.split('\n')

    best_chapter_name = data["items"][0]["snippet"]['title']
    best_chapter_start = 0
    best_chapter_end = float('inf')
    timestamp = timestamp // 1000
    for line in lines:
        
        orig_line = line
        line = line.strip()
        if ':' in line:
            try:
                parts = line.split(' ', 1)
                i = 0
                num_splits = 1
                if not parts[0][0].isdigit() :
                    i=1
                    num_splits = 2
                    parts = line.split(' ', num_splits)
                chapter_timestamp = parts[i].strip()
#                print(chapter_timestamp)
                chapter_name = parts[i+1].strip()
            #print(chapter_timestamp)
            #print(chapter_name)
                chapter_start = convert_timestamp_to_seconds(chapter_timestamp)
                chapter_end = convert_timestamp_to_seconds(lines[lines.index(orig_line) + 1].strip().split(' ', num_splits)[i].strip())
#                print(chapter_end)
            except:
#                print("LOL2")
                continue
#            print(chapter_start)
#            print(chapter_end)
            #and chapter_end - chapter_start < best_chapter_end - best_chapter_start < chapter_end 
            if chapter_start <= timestamp:
                best_chapter_name = chapter_name
                best_chapter_start = chapter_start
                best_chapter_end = chapter_end

    #fix for case when best chapter is last and there is no end time
    if best_chapter_end == float('inf'):
        best_chapter_end = 3599
        try :
            for chapter in chapters_dict["items"][0]["chapters"]["chapters"] :
                chapter_start = chapter["time"]
                if chapter_start <= timestamp:
                    best_chapter_start = chapter_start
                    best_chapter_end = chapters_dict["items"][0]["chapters"]["chapters"][chapters_dict["items"][0]["chapters"]["chapters"].index(chapter) + 1]["time"]
        except:
            best_chapter_end = 3599

    return best_chapter_name, best_chapter_start, best_chapter_end
# const parseChapters = (description) => {
  # // Extract timestamps (either 00:00:00, 0:00:00, 00:00 or 0:00)
  # const lines = description.split("\n")
  # const regex = /(\d{0,2}:?\d{1,2}:\d{2})/g
  # const chapters = []

  # for (const line of lines) {
    # // Match the regex and check if the line contains a matched regex
    # const matches = line.match(regex)
    # if (matches) {
      # const ts = matches[0]
      # const title = line
        # .split(" ")
        # .filter((l) => !l.includes(ts))
        # .join(" ")

      # chapters.push({
        # timestamp: ts,
        # title: title,
      # })
    # }
  # }

  # return chapters
# }


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

def convert_seconds_to_timestamp(seconds):
    hours = seconds // 3600
    minutes = ((seconds % 3600) // 60)
    seconds = seconds % 60
    if hours == 0:
        timestamp = f"{minutes:02d}:{seconds:02d}"
    else:
        timestamp = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return timestamp  

# Function to retrieve the html content of a webpage
def get_html(url):
    response = requests.get(url)
    return response.text

# Function to parse the videoId parameter from a YouTube video URL
def get_video_id(video_url):
    parsed_url = urlparse(video_url)
    print("\n\n",video_url)
    for id in video_url.split("{\"playlistVideoRenderer\":{\"videoId\":\"", video_url.count("{\"playlistVideoRenderer\":{\"videoId\":\"")) :
        video_id = id
        print(video_id)
     
    #video_id =parse_qs(parsed_url.query).get('v')
    if video_id:
        return video_id[0]

# Function to retrieve the best moments for a video
def best_moments(video_id):
    # Your implementation for retrieving the best moments goes here
    vidIdParam = "\n\v" + video_id
    base64_string = base64.b64encode(vidIdParam.encode("utf-8")).decode("utf-8")
    #base64_string = base64.b64encode("\n\vZhT6BeHNmvo".encode("utf-8")).decode("utf-8")
    headers = {
        "Content-Type": "application/json",
    }

    body = json.dumps(
        {
            "context": {"client": {"clientName": "WEB", "clientVersion": "2.9999099"}},
            "params": base64_string,
        }
    )

    response = requests.post(
        "https://www.youtube.com/youtubei/v1/get_transcript?key=AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8",
        headers=headers,
        data=body,
    )

    ##!#!#print(response.text)
    subs_dict = json.loads(response.text)

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! print(json.dumps(subs_dict, indent=4))
    sub_duration = 3600  # 1 hour
    sub_duration = extract_sub_duration(response.text)
    #!#process_default_tier(subtitles)
    ###########
    ##GET INFO:
    ###########
    ###########################

    best_chapter_start = 0
    #best_chapter_end = sub_duration
    best_chapter_name = "hzname"

    start_time = best_chapter_start
    #end_time = best_chapter_end

    result = extract_subtitles(start_time, start_time+600000, response.text)
    #!#!#!#!#!#SELENIUM DETECTED BY TINYWOW( 
    ##!#!
    print("\n\n\n\nSTART ALL\n\n\n\n\n", result)
    ##Segmentation
    #result = text_segmentation(result)
    #print("\n", result)
        # tokenizer = TextTilingTokenizer()
        # tiles = tokenizer.tokenize(result)
        # print("\n", tiles)
    ##
    # for chapter_text in result.split("\n\n") :
        # alachapters_7k = [chapter_text[i:i+7000] for i in range(0, len(chapter_text), 7000)]
        # for alachapter in alachapters_7k:
            # print("\n\n ", alachapter)

    print("\n")
    print("\n\n - Please translate using https://tinywow.com/write/translate or https://tinywow.com/write/ai-rephraser or even https://tinywow.com/write/article-rewriter\n\n")
    ##!#!#!#!#!#fill_edit_field("https://tinywow.com/write/ai-rephraser", "prompt" , result)







    print("######################## info ##############################")
    info_url = 'https://yt.lemnoslife.com/noKey/videos?part=snippet&id=' + video_id
    page_info = requests.get(info_url)
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!print("Result: ", page_info.status_code)
    #print(page_info.text)

    info_dict = json.loads(page_info.text)
    img_url_main = ""
    print("\tVidID: ", video_id)
    try:
        print("\tImageURL: ", info_dict["items"][0]["snippet"]["thumbnails"]["maxres"]["url"])
        img_url_main = info_dict["items"][0]["snippet"]["thumbnails"]["maxres"]["url"]
    except:
        #print("\tImageURL: ", info_dict["items"][0]["snippet"]["thumbnails"]["high"]["url"])
        #img_url_main = info_dict["items"][0]["snippet"]["thumbnails"]["high"]["url"]
        pass
    print("\tTitle: ", info_dict["items"][0]["snippet"]["title"])
    print("\tDescr: \n\n", info_dict["items"][0]["snippet"]["description"])
    print("\n\tPublished: ", datetime.strptime(info_dict['items'][0]['snippet']['publishedAt'][:-1], '%Y-%m-%dT%H:%M:%S').strftime('%#d %B, %Y %I:%M %p'))

        
    ##Get Guest
    if "@" in info_dict["items"][0]["snippet"]["title"]:
        title_parts = info_dict["items"][0]["snippet"]["title"].split('@')
        guest_parts = title_parts[1].split()
        guest = guest_parts[0].strip()
        print('\n\tGuest: youtu.be/@', guest)
    print("\n\tHost: ", info_dict["items"][0]["snippet"]["channelTitle"])
    try:
        print("\tTags: ", info_dict["items"][0]["snippet"]["tags"])
    except:
        print("\tTags: No tags(")

    print("\n######################## chapters ##############################")
    # {
        # "kind": "youtube#videoListResponse",
        # "etag": "NotImplemented",
        # "items": [
            # {
                # "kind": "youtube#video",
                # "etag": "NotImplemented",
                # "id": "NNgYId7b4j0",
                # "chapters": {
                    # "areAutoGenerated": false,
                    # "chapters": [
                        # {
                            # "title": "10- Blue-Eyes Spirit Dragon",
                            # "time": 0,
                            # "thumbnails": [
                                # {
                                    # "url": "https:\/\/i.ytimg.com\/vi\/NNgYId7b4j0\/hqdefault_4000.jpg?sqp=-oaymwEiCKgBEF5IWvKriqkDFQgBFQAAAAAYASUAAMhCPQCAokN4AQ==&rs=AOn4CLCoTrvu0Yu-iNxb7o4II-pxi5WVbQ",
                                    # "width": 168,
                                    # "height": 94
                                # },
                                # {
                                    # "url": "https:\/\/i.ytimg.com\/vi\/NNgYId7b4j0\/hqdefault_4000.jpg?sqp=-oaymwEjCNACELwBSFryq4qpAxUIARUAAAAAGAElAADIQj0AgKJDeAE=&rs=AOn4CLCuupNwIgFIf9hXbjMsvpSGThFyhg",
                                    # "width": 336,
                                    # "height": 188
                                # }
                            # ]
                        # },
                        # {
                            # "title": "9- Invoked Mechaba",
                            # "time": 134,
                            # "thumbnails": [
                                # {
                                    # "url": "https:\/\/i.ytimg.com\/vi\/NNgYId7b4j0\/hqdefault_135933.jpg?sqp=-oaymwEiCKgBEF5IWvKriqkDFQgBFQAAAAAYASUAAMhCPQCAokN4AQ==&rs=AOn4CLBe94BKNpQXvM2dUl75LtcgX0N03w",
                                    # "width": 168,
                                    # "height": 94
                                # },
                                # {
                                    # "url": "https:\/\/i.ytimg.com\/vi\/NNgYId7b4j0\/hqdefault_135933.jpg?sqp=-oaymwEjCNACELwBSFryq4qpAxUIARUAAAAAGAElAADIQj0AgKJDeAE=&rs=AOn4CLBULUhlI1OOjJiW6mpFDUhPzh4Adw",
                                    # "width": 336,
                                    # "height": 188
                                # }
                            # ]
                        # },
                        # ...
                    # ]
                # }
            # }
        # ]
    # }
    chapters_url = 'https://yt.lemnoslife.com/videos?part=chapters&id=' + video_id
    chapters_info = requests.get(chapters_url)
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!print("Result: ", page_info.status_code)
    #print(page_info.text)

    chapters_dict = json.loads(chapters_info.text)
    # try:
    print("\t\nOfficial Chapters:\n")
    i = 1
    for chapter in chapters_dict["items"][0]["chapters"]["chapters"] : 
        print(str(i)+") ",convert_seconds_to_timestamp(chapter["time"]), chapter["title"])
        i = i + 1
    # i = 1
    print("\t\n\nThumbnails: (dsbld)\n")
    # for chapter in chapters_dict["items"][0]["chapters"]["chapters"] : 
    #     #if chapter["thumbnails"][1]["url"].split('?')[0] != img_url_main :
    #     print(str(i)+") ", chapter["thumbnails"][1]["url"])
    #     i = i + 1

    # except:
        # print("\t hui")
        
    ##GET BEST MOMENT:
    #################
    print("\n\n######################## Best Momemt ##############################")
    best_moment_url = 'https://yt.lemnoslife.com/videos?part=mostReplayed&id=' + video_id
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!print("Result: ", page_best_moment_url.status_code)
    #print(page_best_moment_url.text)
    page_best_moment_url = requests.get(best_moment_url)
    best_dict = json.loads(page_best_moment_url.text)
                                                        # subtitles_with_ratings = interpolate_heat_to_subtitles(page_best_moment_url, subtitles)
                                                        # print(subtitles_with_ratings)

    #print(json.dumps(best_dict, indent=4))
    #item["mostReplayed"]["heatMarkers"]["heatMarkerRenderer"]["heatMarkerIntensityScoreNormalized"]
    #for item in best_dict['items']:

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!print(json.dumps(best_dict, indent=4))

    ######################################################################################
    ## WHAAAAT - save gisto as map and spread to raitings of chapters ALLL OF THEM!!!!!!!!
    ######################################################################################
    video_moments = []
    if best_dict['items'][0]['mostReplayed'] is not None:
        i = 1
        for moment in best_dict['items'][0]['mostReplayed']['timedMarkerDecorations']:
            besttimestamp = int(moment['visibleTimeRangeStartMillis']/1000)
            #!#!#for heatMarker in best_dict['items'][0]['mostReplayed']['heatMarkers']:#['markers']
                #!print(heatMarker)
            print("\n\n\tBestMoment", i, str(convert_seconds_to_timestamp(besttimestamp)))
            i = i + 1
            best_chapter_name, best_chapter_start, best_chapter_end = extract_best_chapter(page_info.text, besttimestamp*1000)

            print("\tDirect Link:", "youtube.com/watch?v=" + video_id + "&t=" + str(besttimestamp))
            print("\tTime Range:", convert_seconds_to_timestamp(best_chapter_start), ' - ', convert_seconds_to_timestamp(best_chapter_end))
            print("\tOff BestChapter" + str(i) + "\n", "\t\tName:", best_chapter_name)
            print("\t\tDirect Link:", "youtube.com/watch&v=" + video_id + "&t=" + str(best_chapter_start))
            #!#!print("\n", result)
            result = extract_subtitles(best_chapter_start, best_chapter_end, response.text)
            #!#!#!#!#!#SELENIUM DETECTED BY TINYWOW( 
            print("\t\tText:\n", result)
            video_moments.extend({'best_chapter_name': best_chapter_name, 'best_chapter_start':best_chapter_start,'txt':result,'view_count':i})
        #exit()
        return best_chapter_name, best_chapter_start,
    else :
        print("\tNo BestMoment set(")

# Function to retrieve a minute-long subtitle part and chapter name from video description
#def get_subtitle(video_id, start_time, end_time):
# Your implementation for retrieving the subtitle goes here
def extract_subtitles(start_time, end_time, json_data):
    subtitle_pieces = []
#    subtitles = []

    # Parse the JSON data
    data = json.loads(json_data)

    # Extract the subtitle cues
    cue_groups=[]
    try:
        cue_groups = data['actions'][0]['updateEngagementPanelAction']['content']['transcriptRenderer']['body']['transcriptBodyRenderer']['cueGroups']
    except:
        pass
    text = ""
    # Iterate through each cue group
    for cue_group in cue_groups:
        
        start_offset = cue_group['transcriptCueGroupRenderer']['formattedStartOffset']['simpleText']
        
        # Check if the start offset is within the given range
        if convert_timestamp_to_seconds(start_offset) >= start_time and convert_timestamp_to_seconds(start_offset) < end_time - 1 :
            cues = cue_group['transcriptCueGroupRenderer']['cues']
            
            # Iterate through each cue in the cue group
            for cue in cues:
                cue_duration = cue['transcriptCueRenderer']['durationMs']
                try:
                    cue_text = cue['transcriptCueRenderer']['cue']['simpleText']
                    if cue_text.isupper() :
                        if cue_text.strip() != "AD" :
                            cue_text = " CHAPTER_BRE@K " + cue_text + "."
                        else :
                            cue_text = ""
                    in_a_row = 0
                except:
                    in_a_row = in_a_row + 1
                    if in_a_row > 1 :
                        cue_text = " CHAPTER_BRE@K " + cue_text + "."
                        in_a_row = 0
                    else :
                        continue

                subtitle_pieces.append(cue_text)
#                subtitles.

    subtitle_text = ' '.join(subtitle_pieces)
    return subtitle_text.replace('\n', ' ').replace(' CHAPTER_BRE@K ', '\n\n') #text #, subtitles
#    return subtitle_pieces

# Main function
def main():
    playlist_url = input("Enter the URL of the YouTube playlist: ")
    html_content = get_html(playlist_url)
#    soup = BeautifulSoup(html_content, 'html.parser')
   
    unique_video_ids = set()
    moments = []
   
    # Search for all unique videoId parameters in the playlist
    for link in html_content.split("{\"playlistVideoRenderer\":{\"videoId\":\""):#, soup.text.count("{\"playlistVideoRenderer\":{\"videoId\":\"")) :#.find_all('a'):
        #href = link.get('href')
        video_id = link[0:11]
        #if href.startswith('/watch'):
        #print(link)
        #video_id = get_video_id(href)
        if video_id:
            unique_video_ids.add(video_id)
    
    # Retrieve best moments for each video
    for video_id in unique_video_ids:
        video_moments = best_moments(video_id)
        if video_moments is not None:
            moments.extend(video_moments)
    print(moments)
    # Sort moments by view count
    moments.sort(key=lambda x: x['view_count'], reverse=True)
   
    # Save moments to a CSV file
    with open('best_moments.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['video_id', 'start_time', 'end_time', 'chapter_name', 'view_count'])
        writer.writeheader()
        for moment in moments:
            writer.writerow(moment)

    print("Best moments saved to best_moments.csv")


if __name__ == "__main__":
    main()