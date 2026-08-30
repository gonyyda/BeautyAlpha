import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("YOUTUBE_API_KEY")

channel_id = "UCRiIf6rt91BVfZVtURRXlOw"


# --------------------------------
# 1. 채널 정보 가져오기
# --------------------------------

channel_url = "https://www.googleapis.com/youtube/v3/channels"

channel_params = {
    "part": "snippet,statistics,contentDetails",
    "id": channel_id,
    "key": api_key
}

channel_response = requests.get(
    channel_url,
    params=channel_params
)

channel_data = channel_response.json()

channel = channel_data["items"][0]

channel_name = channel["snippet"]["title"]

subscriber_count = channel[
    "statistics"
].get(
    "subscriberCount",
    "비공개"
)

uploads_playlist_id = channel[
    "contentDetails"
]["relatedPlaylists"]["uploads"]


print()
print("채널명:", channel_name)
print("구독자 수:", subscriber_count)
print()


# --------------------------------
# 2. 최근 업로드 영상 가져오기
# --------------------------------

playlist_url = (
    "https://www.googleapis.com/"
    "youtube/v3/playlistItems"
)

playlist_params = {
    "part": "snippet,contentDetails",
    "playlistId": uploads_playlist_id,
    "maxResults": 30,
    "key": api_key
}

playlist_response = requests.get(
    playlist_url,
    params=playlist_params
)

playlist_data = playlist_response.json()


video_ids = []

for item in playlist_data.get(
    "items",
    []
):
    video_id = item[
        "contentDetails"
    ]["videoId"]

    video_ids.append(video_id)


# --------------------------------
# 3. 영상 조회수 및 길이 가져오기
# --------------------------------

videos_url = (
    "https://www.googleapis.com/"
    "youtube/v3/videos"
)

videos_params = {
    "part": "snippet,statistics,contentDetails",
    "id": ",".join(video_ids),
    "key": api_key
}

videos_response = requests.get(
    videos_url,
    params=videos_params
)

videos_data = videos_response.json()


# --------------------------------
# 4. Shorts 제외
# --------------------------------

long_videos = []

for video in videos_data.get(
    "items",
    []
):

    title = video[
        "snippet"
    ]["title"]

    published_at = video[
        "snippet"
    ]["publishedAt"]

    view_count = int(
        video[
            "statistics"
        ].get(
            "viewCount",
            0
        )
    )

    duration = video[
        "contentDetails"
    ]["duration"]


    # 아주 단순한 1차 필터
    # PT1M 이하 영상은 Shorts 가능성이 높아서 제외
    if duration.startswith("PT"):

        if (
            "M" not in duration
        ):
            continue


    long_videos.append(
        {
            "title": title,
            "published_at": published_at,
            "views": view_count,
            "duration": duration
        }
    )


# --------------------------------
# 5. 최근 일반영상 10개 출력
# --------------------------------

recent_videos = long_videos[:10]

print("최근 일반영상 10개")
print("=" * 70)

for i, video in enumerate(
    recent_videos,
    start=1
):

    print(
        f"{i}. {video['title']}"
    )

    print(
        f"조회수: {video['views']:,}"
    )

    print(
        f"길이: {video['duration']}"
    )

    print(
        f"업로드: {video['published_at']}"
    )

    print("-" * 70)


# --------------------------------
# 6. 평균 / 중앙값 계산
# --------------------------------

if recent_videos:

    views = [
        video["views"]
        for video in recent_videos
    ]

    average_views = (
        sum(views)
        / len(views)
    )

    sorted_views = sorted(views)

    n = len(sorted_views)

    if n % 2 == 1:

        median_views = (
            sorted_views[n // 2]
        )

    else:

        median_views = (
            sorted_views[n // 2 - 1]
            + sorted_views[n // 2]
        ) / 2


    print()
    print("===== 요약 =====")

    print(
        f"평균 조회수: "
        f"{average_views:,.0f}"
    )

    print(
        f"중앙값 조회수: "
        f"{median_views:,.0f}"
    )