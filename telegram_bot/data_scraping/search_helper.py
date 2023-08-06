#search_helper.py
#https://console.cloud.google.com/apis/library/customsearch.googleapis.com?project=speedy-valor-393911
import requests
import json
import base64
import csv
import os

# downloads the first GIF from a Google Images search result and converts it to Base64
GOOGLE_SEARCH_URL = "https://www.googleapis.com/customsearch/v1"
GOOGLE_API_KEY =  os.environ["YOUR_GOOGLE_API_KEY"]
GOOGLE_CX_ID =  os.environ["YOUR_GOOGLE_CX_ID"]
def download_gif(url, output_path):
    response = requests.get(url)
    with open(output_path, "wb") as f:
        f.write(response.content)

def search_and_download_gif(search_query, url_only):
    GOOGLE_API_KEY =  os.environ["YOUR_GOOGLE_API_KEY"]
    GOOGLE_CX_ID =  os.environ["YOUR_GOOGLE_CX_ID"]
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CX_ID,
        "q": search_query,
        "searchType": "image",
        "fileType": "gif",
        "num": 1
    }

    response = requests.get(GOOGLE_SEARCH_URL, params=params)
    data = json.loads(response.text)

    if "items" in data:
        gif_url = data["items"][0]["link"]
        if url_only == True:
            return gif_url
        download_gif(gif_url, search_query + "output.gif")
        return search_query + "output.gif"
    else:
        return None

def convert_gif_to_base64(gif_path):
    with open(gif_path, "rb") as file:
        gif_data = file.read()
        gif_base64 = base64.b64encode(gif_data).decode("utf-8")
        return gif_base64

# TODO: convert back and send through bot

def store_search_result(search_input, gif_base64, csv_file):
    with open(csv_file, "a") as file:
        writer = csv.writer(file)
        writer.writerow([search_input, gif_base64])

if __name__ == '__main__' :
    # Example usage
    search_input = "grid layout" +  " GIF"
    
    csv_file = search_input + "result.csv"

    gif_path = search_and_download_gif(search_input, GOOGLE_API_KEY, GOOGLE_CX_ID)
    if gif_path:
        gif_base64 = convert_gif_to_base64(gif_path)
        store_search_result(search_input, gif_base64, csv_file)
        print("GIF downloaded and stored in CSV file.")
    else:
        print("No GIF found for the search input.")