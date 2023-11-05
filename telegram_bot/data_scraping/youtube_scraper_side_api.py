import requests
import json
import base64
    
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
                chapter_name = parts[i+1].strip()
                chapter_start = convert_timestamp_to_seconds(chapter_timestamp)
                chapter_end = convert_timestamp_to_seconds(lines[lines.index(orig_line) + 1].strip().split(' ', num_splits)[i].strip())
            except:
                continue

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
    
def extract_subtitles(start_time, end_time, json_data):
    subtitle_pieces = []

    # Parse the JSON data
    data = json.loads(json_data)

    # Extract the subtitle cues
    cue_groups = data['actions'][0]['updateEngagementPanelAction']['content']['transcriptRenderer']['body']['transcriptBodyRenderer']['cueGroups']

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


    subtitle_text = ' '.join(subtitle_pieces)
    return subtitle_text.replace('\n', ' ').replace(' CHAPTER_BRE@K ', '\n\n') 
    
    
#start
vidId = '_Zk47-ih9ow'

###############
#video info#####
###############
info_url = 'https://yt.lemnoslife.com/noKey/videos?part=snippet&id=' + vidId


page_info = requests.get(info_url)
info_dict = json.loads(page_info.text)
img_url_main = ""
try:
    print("\tImageURL: ", info_dict["items"][0]["snippet"]["thumbnails"]["maxres"]["url"])
    img_url_main = info_dict["items"][0]["snippet"]["thumbnails"]["maxres"]["url"]
except:
    print("\tImageURL: ", info_dict["items"][0]["snippet"]["thumbnails"]["high"]["url"])
    img_url_main = info_dict["items"][0]["snippet"]["thumbnails"]["high"]["url"]
print("\tTitle: ", info_dict["items"][0]["snippet"]["title"])
print("\tDescr: \n\n", info_dict["items"][0]["snippet"]["description"])
print("\n\tPublished", datetime.strptime(info_dict['items'][0]['snippet']['publishedAt'][:-1], '%Y-%m-%dT%H:%M:%S').strftime('%#d %B, %Y %I:%M %p'))

    
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

###############
#GET chapters:
###############
print("\n######################## chapters ##############################")
chapters_url = 'https://yt.lemnoslife.com/videos?part=chapters&id=' + vidId
chapters_info = requests.get(chapters_url)

chapters_dict = json.loads(chapters_info.text)

print("\tOfficial Chapters:")
for chapter in chapters_dict["items"][0]["chapters"]["chapters"] : 
    print("\t", convert_seconds_to_timestamp(chapter["time"]), chapter["title"])
    if chapter["thumbnails"][1]["url"].split('?')[0] != img_url_main :
        print("\t\t", chapter["thumbnails"][1]["url"], "\n")  
        
###############
#GET SUBTITLES:
###############
vidIdParam = "\n\v" + vidId
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

response = requests.post(
    "https://www.youtube.com/youtubei/v1/get_transcript?key=AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8",
    headers=headers,
    data=body,
)

subs_dict = json.loads(response.text)
sub_duration = 3600  # 1 hour
sub_duration = extract_sub_duration(response.text)

best_chapter_start = 0
best_chapter_end = sub_duration
subs_text = extract_subtitles(best_chapter_start, best_chapter_end, response.text)

###############
#besttimestamp#
###############
best_moment_url = 'https://yt.lemnoslife.com/videos?part=mostReplayed&id=' + vidId
page_best_moment_url = requests.get(best_moment_url)
best_dict = json.loads(page_best_moment_url.text)
besttimestamp = convert_timestamp_to_seconds('4:20') * 1000
best_chapter_name = "hzname"
if best_dict['items'][0]['mostReplayed'] is not None and n == 2:
    i = 1
    for moment in best_dict['items'][0]['mostReplayed']['timedMarkerDecorations']:
        besttimestamp = moment['visibleTimeRangeStartMillis']

        print("BestMoment_Timestamp ", i, besttimestamp/1000)
        i = i + 1
        best_chapter_name, best_chapter_start, best_chapter_end = extract_best_chapter(page_info.text, besttimestamp)


def extract_sub_duration(json_data):
    # Parse the JSON data
    data = json.loads(json_data)
    last_timestamp = 0
    # Extract the subtitle cues
    try:
        cue_groups = data['actions'][0]['updateEngagementPanelAction']['content']['transcriptRenderer']['body']['transcriptBodyRenderer']['cueGroups']
        
        last_timestamp = convert_timestamp_to_seconds(cue_groups[len(cue_groups) - 1]['transcriptCueGroupRenderer']['formattedStartOffset']['simpleText'])
    except:
        sys.exit("FUCK NO SUBS(")
        
    return last_timestamp
    
def convert_seconds_to_timestamp(seconds):
    hours = seconds // 3600
    minutes = ((seconds % 3600) // 60)
    seconds = seconds % 60
    if hours == 0:
        timestamp = f"{minutes:02d}:{seconds:02d}"
    else:
        timestamp = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return timestamp 
    
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