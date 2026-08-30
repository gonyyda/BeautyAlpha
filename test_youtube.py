import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("YOUTUBE_API_KEY")

if not api_key:
    print("API 키를 찾을 수 없습니다.")
    exit()

url = "https://www.googleapis.com/youtube/v3/search"

params = {
    "part": "snippet",
    "q": "K-beauty",
    "type": "video",
    "maxResults": 5,
    "key": api_key
}

response = requests.get(url, params=params)

print("상태 코드:", response.status_code)
print(response.json()) 