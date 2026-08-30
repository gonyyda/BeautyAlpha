import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("YOUTUBE_API_KEY")

search_name = "강민경"

url = "https://www.googleapis.com/youtube/v3/search"

params = {
    "part": "snippet",
    "q": search_name,
    "type": "channel",
    "maxResults": 5,
    "key": api_key
}

response = requests.get(url, params=params)

data = response.json()

print(f"\n'{search_name}' 검색 결과\n")

for item in data.get("items", []):
    channel_id = item["snippet"]["channelId"]
    channel_title = item["snippet"]["channelTitle"]
    description = item["snippet"]["description"]

    print("채널명:", channel_title)
    print("채널 ID:", channel_id)
    print("설명:", description[:100])
    print("-" * 50)