#Install chrome driver for autopopup https://chromedriver.storage.googleapis.com/index.html?path=114.0.5735.90/

# hello database architecture specialist, please help with implementation of specially thought out storage architecture. imagine this, you have automatically generated subtitles from youtube video, and an ability to rephrase text in 2 ways: first mode acts almost literarly, fixing grammar an translatiing, in a way that it preserves all actual sentenses, reformulated from casual speach to more official looking, and second way - length of the text reduced couple of times in length and main message generalised respectively. help me implement following idea using python script and json: 
# input - list of subtitle items, with following attributes:
# timestamp_start,
# timestamp_end,
# message,
# and two non trivial ones:
# replayabily_rating
# and most importantly "tier" attribute, this is the main idea of proposed architecture: tier parameter initially is empty, it is generated and used during initial data cooking.
# replayability raiting one will be explained later, just let it be for now. now, about the Tier parameter, you can compare it to header in html, like h1 h2 h3 h4. where the higher the tier the shorter and more general is the message - imagine initially we have only lets name it "zero" tier messages timestamped from the start and end. we ned such architecture that we shoul be able to generate and store timestamped messages of higher and higher tiers in the same table, can you believe it, i think you'll also think that it's genious at the end)
# so, let me explain how initial processing of  input subtitles is expected, and you will think how to implement it, ok? 
# so "default" tier messages, first get their "timestamp_end" calculated as equal to start of next message of the same default tier. 
# next, we need to devide text, combined by concatenating all initial messages into chunks about 2000 symbols - create "chapter" message items with this parts of text, right, "chapter" messages will be saved in same table as default tier. 
# and also generate timestamps of start and end, which are set equal to start of first included messagege and end timestamp equal to last included message of default tier. 
# this text is then presented to script user to be rephrased or translated in first explained way, we'll get correct sentances with correct grammar and punctuation later - just prepare placeholders for messages itselves.
# and calculate timestamp_start and timestamp_end right away for  paragraph_set tier items, respectively to "chapter" items from which they we originally copied.

# on second pass, "paragraph_set" items will be already present, so we need second function to parse back "paragraph_set" items and generate "paragraph" items.
# first, devide this "paragraph_set" items by paragraphs, i mean by "\n" and save separately as tier "paragraphs" items.
# calculate timestamp_start and timestamp_end for them by interpolating from paragraph_set proportionally: 
# (paragraphs length + length of previous paragraphs)*(paragraph_set's timestamp_end-timestamp_start)/(paragraph_set's string lenth) for each paragraph.
# devide this message by paragraphs, and save separately as "paragraph" tier messages with timestamps assigned by interpolating equally between paragraph_set's timestamp_start and timestamp_end transphrased timestamps.

# Table as example for better understanding

# tier		    |msg_eng		  |timestamp_start 						 |timestamp_end									  |message_ru |message_ua |rating
# ________________|_________________|______________________________________|________________________________________________|___________|___________|______
 # "default"	    | bla			  | [first pass input]					 | calculated = from n + 1 of same tier			  |			  |           | [first pass input]
 # "chapter"      | ' '.join()	  | copy from respective included default| copy from respective last included default	  |			  |			  | 
 # "paragraph_set"| [2nd pass input]| copy from "chapter" right away		 | copy from respective "chapter"			 	  |			  |			  | 
 # "paragraph"	| devide by "\n"  | calculated, described above 	 	 | copy from timestamp_start of the next paragraph| translated| translated| get interpolated value from time/rating map by copyed timestamps

# We will need a function to combine "default" subtitle items into "chapters" - just count 2000 characters, lol
# Following function add_subtitles_to_chapters(chapters, subtitles) is an example for case when for chapters timstamp_start values are predefined, so concatination of "default" subtitle items into "chapter" can be done by just comparing by timing wether it contains "default" item or not:




# In this add_subtitles_to_chapters(chapters, subtitles) function, we iterate over the chapters and for each chapter, we determine the start and end timestamps based on the chapter timestamps. We then iterate over the original subtitles and check if the subtitle timestamp falls within the time period of the current chapter. If it does, we add the subtitle to the list of subtitles for that chapter, along with its timestamp. Finally, we return the rearranged subtitles as a list of tuples where the first element is the chapter title and the second element is a list of tuples containing the subtitle timestamps and texts.

# The add_subtitles_to_chapters function takes two arguments: chapters and subtitles. It rearranges the subtitles into chapters based on the timestamps provided in the chapters list.

# Here's a step-by-step explanation of how the function works:

# 1. It initializes an empty list called chapter_and_rearranged_subtitles to store the rearranged subtitles.

# 2. It iterates over the chapters list using a for loop and the range function. The loop variable i represents the index of the current chapter.

# 3. Inside the loop, it retrieves the timestamp and title of the current chapter using the chapters[i] syntax. It assigns them to the variables chapter_timestamp_start and chapter_title, respectively.

# 4. It determines the start and end timestamps for the current chapter. The start timestamp is set to chapter_timestamp_start, and the end timestamp is set to chapters[i+1][0] if i+1 is less than the length of chapters. Otherwise, it is set to None. This logic ensures that the last chapter does not have an end timestamp.

# 5. It initializes an empty list called chapter_subtitles to store the subtitles for the current chapter.

# 6. It iterates over the subtitles list using a for loop. The loop variable subtitle represents each subtitle item, which is a tuple containing the subtitle text and timestamp.

# 7. Inside the loop, it checks if the subtitle timestamp falls within the time period of the current chapter. It does this by comparing the subtitle timestamp with the chapter start and end timestamps. If the subtitle timestamp is greater than or equal to the start timestamp and less than the end timestamp (or if the end timestamp is None), it means the subtitle belongs to the current chapter.

# 8. If the subtitle belongs to the current chapter, it appends a tuple containing the subtitle timestamp and text to the chapter_subtitles list.

# 9. After iterating over all the subtitles, it appends a tuple containing the chapter title and the chapter_subtitles list to the chapter_and_rearranged_subtitles list.

# 10. Finally, it returns the chapter_and_rearranged_subtitles list, which contains the rearranged subtitles grouped by chapters.

# Note that the code assumes that the chapters list is sorted in ascending order of timestamps and that the subtitles list is also sorted in ascending order of timestamps.

# Let me know if you have any further questions!
# Sure, I can help you with implementing the storage architecture for your subtitles using Python and JSON. Let's break down the steps and discuss how to implement them.

# 1. Initial Processing of Default Tier Messages:
   # - Calculate the timestamp_end for each default tier message as the start of the next message of the same default tier.
   # - Concatenate all initial messages into chunks of about 2000 characters and create "chapter" message items with these parts of text.
   # - Save the "chapter" messages in the same table as the default tier.
   # - Generate timestamp_start and timestamp_end for the "chapter" items, where timestamp_start is set equal to the start of the first included message and timestamp_end is set equal to the end of the last included message of the default tier.

# 2. Rephrasing and Translating:
   # - Present the concatenated text from the "chapter" items to the script user to be rephrased or translated in the first explained way.
   # - Prepare placeholders for the messages themselves, as we will add correct sentences with correct grammar and punctuation later.

# 3. Calculation of Timestamps for Paragraph Set Tier Items:
   # - On the second pass, the "paragraph_set" items will already be present.
   # - Create a second function to parse back the "paragraph_set" items and generate "paragraph" items.
   # - Divide the "paragraph_set" items by paragraphs (using "\n") and save them separately as "paragraphs" tier items.
   # - Calculate timestamp_start and timestamp_end for each paragraph by interpolating from the paragraph_set proportionally. You can use the formula: (paragraphs_length + length_of_previous_paragraphs) * (paragraph_set_timestamp_end - paragraph_set_timestamp_start) / paragraph_set_string_length.
   # - Divide the message by paragraphs and save them separately as "paragraph" tier messages with timestamps assigned by interpolating equally between the paragraph_set's timestamp_start and timestamp_end.

# Here's an example table to help you understand the structure:

# | tier            | msg_eng            | timestamp_start                | timestamp_end                       | message_ru | message_ua | rating                       | ... |
# |-----------------|--------------------|--------------------------------|-------------------------------------|------------|------------|------------------------------|-----|
# | "default"       | bla                | [first pass input]             | calculated = from n + 1 of same tier|            |            | [first pass input] 
# | "chapter"       | ' '.join()         | ... |
# | "paragraph_set" | [2nd pass input]   | copy from "chapter" right away | copy from respective "chapter"      |            |            |                              | ... |
# | "paragraph"     |                    |                                |                                     |            |            |                              | ... |

#from bs4 import BeautifulSoup
from googletrans import Translator
from googleapiclient.discovery import build
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import csv
import requests
import base64
import json
import sys
import re
from datetime import datetime
import time
import webbrowser
import nltk
from nltk.tokenize import sent_tokenize
from nltk.tokenize.punkt import PunktSentenceTokenizer
from nltk.tokenize import TextTilingTokenizer
#NOTE" uncomment once to download models for text chapter parcer nltk.download()
#import numpy as np
#from fuzzywuzzy import fuzz
#with open('fcc.json', 'r') as fcc_file:
#    fcc_data = json.load(fcc_file)
#    print(fcc_data)
#import urllib2

                                                                            # def open_link_in_browser(url):
                                                                                # webbrowser.open(url)

                                                                            ##Example usage
                                                                            # url = 'https://www.example.com'
                                                                            # open_link_in_browser(url)
                                                                            
                                                                            
                                                                            
                                                                            
#Example usage
# url = 'https://www.example.com'
# field_id = 'edit-field-id'
# text = 'Hello, world!'
# fill_edit_field(url, field_id, text)                                                                            
def fill_edit_field(url, field_id, text):
    webbrowser.register('chrome', None, webbrowser.BackgroundBrowser("C://Program Files (x86)//Google//Chrome//Application//chrome.exe"))
    webbrowser.get('chrome').open(url)
    translated_str = str(input())
    # driver = webdriver.Chrome()
    # driver.get(url)
    # time.sleep(5)
    # edit_field = driver.find_element("id", field_id)
    # edit_field.send_keys(text)

	
# 

# Example usage
# url = 'https://www.example.com'
# field_id = 'edit-field-id'
# text_value = get_text_from_edit_field(url, field_id)
# print(text_value)
def get_text_from_edit_field(url, field_id):
    driver = webdriver.Chrome("C:/chromedriver.exe")  # Replace with the appropriate driver for your browser
    driver.get(url)

    #Wait for the edit field to appear and retrieve its text value
    edit_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, field_id))
    )
    text_value = edit_field.get_attribute('value')

    return text_value

                                                                    



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


# subtitle_pieces_with_timestamps = [
        # ("Subtitle 1", "00:00")
    # ]
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
        
#    print("LOLOLO",cue_groups[len(cue_groups) - 1]['transcriptCueGroupRenderer']['formattedStartOffset']['simpleText'])
    return last_timestamp
    
def extract_subtitles(start_time, end_time, json_data):
    subtitle_pieces = []
#    subtitles = []

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
#                subtitles.

    subtitle_text = ' '.join(subtitle_pieces)
    return subtitle_text.replace('\n', ' ').replace(' CHAPTER_BRE@K ', '\n\n') #text #, subtitles
#    return subtitle_pieces

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
    
def extract_chapters_by_questions(text, duration):
    # Split the text into sentences
    sentences = re.split(r"(?<=[.!?])\s+", text)
    
    chapters = []
    sentance_counter = 0
    
    for sentence in sentences:
        # Check if the sentence is a question
#        print("LOLOLO",sentence)
        if sentence.endswith('?'):
            chapter_title = sentence.strip()
            chapter_timestamp = convert_seconds_to_timestamp(sentance_counter  * duration // len(sentences))
            if chapter_title.isupper() : 
                chapters.append(chapter_timestamp, chapter_title) 
            else : 
                chapters.append((chapter_timestamp, sentences[sentences.index(sentence) - 1] + " " + chapter_title))
        
        sentance_counter = sentance_counter + 1
    
    return chapters

def divide_text_into_chapters_keyword_based(text, keywords):
    chapters = []
    current_chapter = []
    
    for sentence in text.split('.'):
        sentence = sentence.strip()
        if any(keyword in sentence for keyword in keywords):
            if current_chapter:
                chapters.append(' '.join(current_chapter))
                current_chapter = []
        current_chapter.append(sentence)
    
    if current_chapter:
        chapters.append(' '.join(current_chapter))
    
    return chapters
    
def divide_text_into_chapters_text_segmentationHZ(text):
    chapters = []
    tokenizer = PunktSentenceTokenizer()
    boundaries = tokenizer.span_tokenize(text)
    start = 0
    
    for boundary in boundaries:
        chapter_text = text[start:boundary[1]].strip()
        chapters.append(chapter_text)
        start = boundary[1]
    
    return chapters
    
def text_segmentation(text):
    # Tokenize the text into paragraphs
    paragraphs = text.split('\n\n')

    # Initialize the TextTiling tokenizer
    tokenizer = TextTilingTokenizer()
    tokenizer = nltk.data.load('nltk:tokenizers/punkt/english.pickle')

    # Segment each paragraph using TextTiling
    segmented_text = []
    for paragraph in paragraphs:
        if len(paragraph) < 10:
            segmented_text.append(paragraph)
        else:
            tiles = tokenizer.tokenize(paragraph)
            segmented_text.extend(tiles)
            print(tiles[0])

    # Join the segmented text back into a single string
    segmented_text = '\n\n'.join(segmented_text)

    return segmented_text

def add_subtitles_to_chapters(chapters, subtitles):
    # Create a list to store the rearranged subtitles
    chapter_and_rearranged_subtitles = []
    
    # Iterate over the chapters
    for i in range(len(chapters)):
        chapter_timestamp_start, chapter_title  = chapters[i]
        
        # Get the start and end timestamps for the current chapter
        start_timestamp = chapter_timestamp
        chapter_timestamp_end = chapters[i+1][0] if i+1 < len(chapters) else sub_duration
        
        # Initialize an empty list for the subtitles of the current chapter
        chapter_subtitles = []
        
        # Iterate over the original subtitles
        for subtitle in subtitles:
            subtitle_text, subtitle_timestamp = subtitle
            
            # Check if the subtitle timestamp falls within the chapter's time period
            if chapter_timestamp_end is None or chapter_timestamp_start <= subtitle_timestamp < chapter_timestamp_end:
                chapter_subtitles.append((subtitle_timestamp_start, subtitle_text))
        
        # Add the chapter and its subtitles to the chapter_and_rearranged_subtitles list
        chapter_and_rearranged_subtitles.append((chapter_title, chapter_subtitles))
    
    return chapter_and_rearranged_subtitles
    

#Please let me know if you have any specific questions or if there's anything else I can assist you with!
###thanks, greate explanation of steps, now please implement each step in python as functions, please
#Sure! I'd be happy to help you implement each step as functions in Python. Let's start with the initial processing of the default tier messages. Here's a function that takes a list of subtitle items and performs the necessary calculations and transformations:

#This function takes a list of subtitle items as input and returns a new list of processed subtitle items. It calculates the timestamp_end for each default tier message based on the length of the message and the replayability_rating. It then divides the message into chunks of 2000 characters and generates start and end timestamps for each chunk. The processed subtitle items are added to the processed_subtitles list.
def process_default_tier(subtitles):
    processed_subtitles = []
    timestamp_end = 0
    iter=0

    for subtitle in subtitles:
        iter = iter +1
        # Calculate timestamp end for default tier messages
        timestamp_end = subtitles[iter][0] if iter < len(subtitles) else sub_duration

        # Divide the text into chunks of 2000 characters to create "chapter" messages
        
        subtitle_text, subtitle_timestamp = subtitle
        chunks = [subtitle['message'][i:i+2000] for i in range(0, len(subtitle['message']), 2000)]

        # Generate start and end timestamps for the "chapter" messages
        timestamp_start = subtitle['timestamp_start']
        for chunk in chunks:
            chapter = {
                'timestamp_start': timestamp_start,
                'timestamp_end': timestamp_end,
                'message': chunk,##later article - article name will become chapter name
                'tier': subtitle['tier']
            }
            processed_subtitles.append(chapter)
        
    return processed_subtitles




#Next, let's implement a function to parse back the "paragraph_set" items and generate "paragraph" items. This function will be called for subtitle items with the tier parameter set to "paragraph_set". Here's the code:
#This function takes a list of subtitle items as input and returns a new list of processed subtitle items. It splits the message of each "paragraph_set" item into paragraphs using the split('\n\n') method. It then calculates the start and end timestamps for each paragraph

def process_paragraph_set_tier(subtitles):
    processed_subtitles = []

    for subtitle in subtitles:
        # Divide the "paragraph_set" item by paragraphs
        paragraphs = subtitle['message'].split('\n\n')

        # Calculate timestamps for each paragraph
        timestamp_start_bak = subtitle['timestamp_start'] 
        for paragraph in paragraphs:
            paragraph_item = {
                'timestamp_start': timestamp_start_bak,  
                'timestamp_end': timestamp_start_bak + len(paragraph) * ( convert_timestamp_to_seconds(subtitle['timestamp_end']) - convert_timestamp_to_seconds(subtitle['timestamp_start'])) / len(subtitle['message']),
                'message': paragraph,
                'tier': 'paragraph'
            }
            timestamp_start_bak = paragraph_item['timestamp_end']
            processed_subtitles.append(paragraph_item)
            
            # Extract the first sentence as the chapter
            chapter_name = re.split(r'(?<=[.!?])\s+', paragraph.strip())[0]
            #Generate start and end timestamps for the "chapter" messages
            timestamp_start = subtitle['timestamp_start']
            chapter = {
                'timestamp_start': paragraph_item['timestamp_start'],
                'timestamp_end': paragraph_item['timestamp_end'],
                'message': chapter_name,
                'tier': 'chapter'
            }
            processed_subtitles.append(chapter)

    return processed_subtitles.split('\n\n')

#These two functions should help you with the initial processing of the subtitle items. Let me know if you have any questions or if there's anything else I can assist you with!

def interpolate_heat_to_subtitles(histogram_data, subtitles):
    # Load histogram data
    histogram = json.loads(histogram_data)
    
    # Extract heatMarkers from the histogram data
    heat_markers = histogram['items'][0]['mostReplayed']['heatMarkers']
    
    # Iterate over subtitles
    for subtitle in subtitles:
        start_time = subtitle['start_time']
        end_time = subtitle['end_time']
        
        # Find maximum heat the corresponding heat marker for the subtitle
        subtitle['chapter_coolness_rating'] = find_max_heat_marker(heat_markers, start_time, end_time)
    
    return subtitles

def find_max_heat_marker(heat_markers, start_time, end_time):
    max_heat = 0.0
    for heat_marker in heat_markers:
        marker_start = heat_marker['heatMarkerRenderer']['timeRangeStartMillis']
        marker_end = marker_start + heat_marker['heatMarkerRenderer']['markerDurationMillis']
        
        if start_time <= marker_start and end_time >= marker_end and max_heat < heat_marker['heatMarkerRenderer']['heatMarkerIntensityScoreNormalized']:
            max_heat = heat_marker['heatMarkerRenderer']['heatMarkerIntensityScoreNormalized']
    
    return max_heat



#######
##MAIN:
#######
print("\n#############################################################")
print("######################## start ##############################")
print("#############################################################")
#url = 'https://www.youtube.com/@ABCNews'
vidId = '_Zk47-ih9ow'
besttimestamp = convert_timestamp_to_seconds('4:20') * 1000
n = len(sys.argv)
if n > 1 :
    vidId = sys.argv[1][-11:]
    if n > 2 :
        besttimestamp = convert_timestamp_to_seconds(sys.argv[2]) * 1000
        
        
###############
#GET SUBTITLES:
###############
print("####################### all subs ############################")
        #curl -s 'https://www.youtube.com/youtubei/v1/get_transcript?key=AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8' -H 'Content-Type: application/json' --data-raw "{\"context\":{\"client\":{\"clientName\":\"WEB\",\"clientVersion\":\"2.9999099\"}},\"params\":\"$(printf '\n\x0bVIDEO_ID' | base64)\"}"
        # url = 'https://www.youtube.com/youtubei/v1/get_transcript?key=AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8'
        # complex_param = "{\"context\":{\"client\":{\"clientName\":\"WEB\",\"clientVersion\":\"2.9999099\"}},\"params\":\"$(printf '\n\x0b" + vidId + "' | base64)\"}"
        #req = urllib2.Request(url, complex_param, {'Content-Type': 'application/json'})
        #f = urllib2.urlopen(req)
        #for x in f:
        #    print(x)
        #f.close()

vidIdParam = "\n\v" + vidId
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
best_chapter_end = sub_duration
best_chapter_name = "hzname"

start_time = best_chapter_start
end_time = best_chapter_end

result = extract_subtitles(start_time, end_time, response.text)
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
info_url = 'https://yt.lemnoslife.com/noKey/videos?part=snippet&id=' + vidId
page_info = requests.get(info_url)
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!print("Result: ", page_info.status_code)
#print(page_info.text)

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
chapters_url = 'https://yt.lemnoslife.com/videos?part=chapters&id=' + vidId
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
best_moment_url = 'https://yt.lemnoslife.com/videos?part=mostReplayed&id=' + vidId
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
if best_dict['items'][0]['mostReplayed'] is not None and n == 2:
    i = 1
    for moment in best_dict['items'][0]['mostReplayed']['timedMarkerDecorations']:
        besttimestamp = int(moment['visibleTimeRangeStartMillis']/1000)
        #!#!#for heatMarker in best_dict['items'][0]['mostReplayed']['heatMarkers']:#['markers']
            #!print(heatMarker)
        print("\n\n\tBestMoment", i, str(convert_seconds_to_timestamp(besttimestamp)))
        i = i + 1
        best_chapter_name, best_chapter_start, best_chapter_end = extract_best_chapter(page_info.text, besttimestamp*1000)

        print("\tDirect Link:", "youtube.com/watch?v=" + vidId + "&t=" + str(besttimestamp))
        print("\tTime Range:", convert_seconds_to_timestamp(best_chapter_start), ' - ', convert_seconds_to_timestamp(best_chapter_end))
        print("\tOff BestChapter" + str(i) + "\n", "\t\tName:", best_chapter_name)
        print("\t\tDirect Link:", "youtube.com/watch&v=" + vidId + "&t=" + str(best_chapter_start))
        #!#!print("\n", result)
        result = extract_subtitles(best_chapter_start, best_chapter_end, response.text)
        #!#!#!#!#!#SELENIUM DETECTED BY TINYWOW( 
        print("\t\tText:\n", result)
    exit()
else :
    print("\tNo BestMoment set(")

    print("\n\n######### default ###################")
    print("######### default ###################")
    print("######### default ###################")

    #start_time = convert_timestamp_to_seconds('00:05')
    #end_time = convert_timestamp_to_seconds('00:30')

    start_time = best_chapter_start
    end_time = best_chapter_end
    ##!#!# result = extract_chapters_by_questions(start_time, end_time, response.text)
    best_chapter_name, best_chapter_start, best_chapter_end = extract_best_chapter(page_info.text, besttimestamp)


    ############### WHAAAATTTTT ########################
    # Split the text into subtitles
    #subtitles = re.split(r'(?<=[.!?])\s+', page_info.text)

    ############### \WHAAAATTTTT ########################
    print("\n\tTime Range:", convert_seconds_to_timestamp(best_chapter_start), ' - ', convert_seconds_to_timestamp(best_chapter_end))
    print("\n\tBest Chapter Name:", best_chapter_name)
    #!#!print("\n", result)
    result = extract_subtitles(best_chapter_start, best_chapter_end, response.text)
    #!#!#!#!#!#SELENIUM DETECTED BY TINYWOW( 
    print("\n\tBest Chapter Text:\n\n", result)



exit()
print("\n\n## continue? #")
input()
##CHAPGEN
#########
print("\n\n - Input rephrased with questions, for chapter extraction:?\n")
rephrased_str = str(input())
chapters = extract_chapters_by_questions(rephrased_str, sub_duration)
##!#!chapters = divide_text_into_chapters_text_segmentation(rephrased_str)
print("\n## CHAPGEN ###############", sub_duration)
#!#!#!#!
# for chapter in chapters:
    # print(chapter[0], chapter[1])
# alachapter_by_questions = rephrased_str.split('?')
# for alachapter in alachapter_by_questions:
    # print("\n\n ", alachapter)
    
for chapter in chapters:
    print(chapter[0], chapter[1])
print("\n\n## \CHAPGEN ##############")

##Rus Version:
###################################
print("\n\tRus Version:")
lines_rus = result.split('.')
for line_rus in lines_rus:
    print("\n", lines_rus.index(line_rus) + 1, "\n",  convert_seconds_to_timestamp((end_time - start_time) * lines_rus.index(line_rus) // len(lines_rus)), "-->", convert_seconds_to_timestamp((end_time - start_time) * (lines_rus.index(line_rus) + 1) // len(lines_rus) - 1), "\n", line_rus)
print("\n\n", result)
print("\n########################                          ###########################")

#English Version:
###################################
translator = Translator()
print("\n\tEnglish Version:")
try:
    result_eng = translator.translate(result, src='ru', dest='en')
    lines_eng = result_eng.text.split('.')
    for line_eng in lines_eng:
        print("\n", lines_eng.index(line_eng) + 1, "\n",  convert_seconds_to_timestamp((end_time - start_time) * lines_eng.index(line_eng) // len(lines_eng)), "-->", convert_seconds_to_timestamp((end_time - start_time) * (lines_eng.index(line_eng) + 1) // len(lines_eng) - 1), "\n", line_eng)
    print("\n\n", result_eng.text)
except:
    #try by sentense
    lines_eng = result.split('.')
    for line_eng in lines_eng:
        print("\n\n")
        #, translator.translate(line_eng[0:420], src='ru', dest='en').text)
#    result = translator.translate(result[0:300], src='ru', dest='en')
#best_chapter_name_EN = translator.translate(best_chapter_name, src='ru', dest='en')
#print("\nBest Chapter Name:", best_chapter_name_EN.text)
#print(result.text)


print("\n\n\t################ https://tinywow.com/write/ai-rephraser 7.5k also translates #############")
print("\t################ https://tinywow.com/write/shorten-content 3k  ##########################")
print("\t################ https://tinywow.com/write/content-summarizer 3k beautify chapgen #######")
print("\t################ https://tinywow.com/write/translate 2k #################################")
print("\n\n\t################ https://tinywow.com/write/article-rewriter 7.5k turn into article after initial refrasing/translation #########")
print("\t################ https://tinywow.com/tools/write #########################")
print("\t################ https://tinywow.com/write/sentence-rewriter 300 #########")
print("\t################ https://tinywow.com/write/business-plan-generator ) #####")


print("\n\n - Enter rensphrased text to regen subtitles:\n")
rephrased_str = str(input())
rephrased = rephrased_str.split('.')
for rephrased_line in rephrased:
    print("\n", rephrased.index(rephrased_line) + 1, "\n",  convert_seconds_to_timestamp((end_time - start_time) * rephrased.index(rephrased_line) // len(rephrased)), "-->", convert_seconds_to_timestamp((end_time - start_time) * (rephrased.index(rephrased_line) + 1) // len(rephrased) - 1), "\n", rephrased_line)