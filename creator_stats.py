import os
import requests
import statistics
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("YOUTUBE_API_KEY")

if not api_key:
    print("YouTube API 키를 찾을 수 없습니다.")
    exit()


# --------------------------------
# 크리에이터 목록
# --------------------------------

creators = {
    # 뷰티 전문
    "지냐": "UCRiIf6rt91BVfZVtURRXlOw",
    "민스코": "UCTQGAYPtbnCEfW9IGx65kiw",
    "아랑": "UCY2YdDn7zXtRbNR0fJ9V_YQ",
    "유트루": "UCH2mJnztSdNh8ADp2KmtUMQ",
    "레오제이": "UCnFFOjljp1_sacTz7PfIIyg",
    "디렉터파이": "UCqrNqg3UgVoD3Sa-F_TxuSA",
    "회사원A": "UCnekLiljel-Px4ClMC7b3mg",

    # 대중 인플루언서
    "프리지아": "UCAbhooUR9thtUYAkLxk9iBg",
    "성해은": "UCI5ZLTYfIfXaeubb2ny0kNA",
    "박지현": "UC0JEvlaTw-nX7iDLb_L_ymA",
    "민와와": "UCJt-9Ku_D1Un6brccoTzglg",
    "퀸승용": "UCjqPJOm46V1pO_ffHoqrXow",
    "박현지": "UCmdOnmYKm4hijBxwGHtPT8Q",
    "지연이라면": "UCnwu3n--W9bbMsKQGyybKSQ",
    "걍밍경": "UCfqVrM2cvwxG3-EvxbsN0KQ",
}

# --------------------------------
# ISO 8601 영상 길이를 초로 변환
# 예: PT2M15S -> 135초
# --------------------------------

def duration_to_seconds(duration):

    duration = duration.replace("PT", "")

    hours = 0
    minutes = 0
    seconds = 0

    if "H" in duration:
        parts = duration.split("H")
        hours = int(parts[0])
        duration = parts[1]

    if "M" in duration:
        parts = duration.split("M")
        minutes = int(parts[0])
        duration = parts[1]

    if "S" in duration:
        seconds = int(duration.replace("S", ""))

    total_seconds = (
        hours * 3600
        + minutes * 60
        + seconds
    )

    return total_seconds


# --------------------------------
# 한 채널 분석 함수
# --------------------------------

def analyze_creator(channel_id):

    # 1. 채널 정보
    channel_url = (
        "https://www.googleapis.com/youtube/v3/channels"
    )

    channel_params = {
        "part": "snippet,statistics,contentDetails",
        "id": channel_id,
        "key": api_key
    }

    channel_response = requests.get(
        channel_url,
        params=channel_params
    )

    channel_response.raise_for_status()

    channel_data = channel_response.json()

    if not channel_data.get("items"):
        return None

    channel = channel_data["items"][0]

    channel_name = channel[
        "snippet"
    ]["title"]

    subscriber_count = int(
        channel[
            "statistics"
        ].get(
            "subscriberCount",
            0
        )
    )

    uploads_playlist_id = channel[
        "contentDetails"
    ][
        "relatedPlaylists"
    ][
        "uploads"
    ]


    # --------------------------------
    # 2. 최근 업로드 50개 가져오기
    # --------------------------------

    playlist_url = (
        "https://www.googleapis.com/youtube/v3/playlistItems"
    )

    playlist_params = {
        "part": "contentDetails",
        "playlistId": uploads_playlist_id,
        "maxResults": 50,
        "key": api_key
    }

    playlist_response = requests.get(
        playlist_url,
        params=playlist_params
    )

    playlist_response.raise_for_status()

    playlist_data = playlist_response.json()

    video_ids = []

    for item in playlist_data.get(
        "items",
        []
    ):
        video_ids.append(
            item[
                "contentDetails"
            ][
                "videoId"
            ]
        )

    if not video_ids:
        return None


    # --------------------------------
    # 3. 영상 세부정보
    # --------------------------------

    videos_url = (
        "https://www.googleapis.com/youtube/v3/videos"
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

    videos_response.raise_for_status()

    videos_data = videos_response.json()


    # --------------------------------
    # 4. 일반영상 필터
    # --------------------------------

    long_videos = []

    for video in videos_data.get(
        "items",
        []
    ):

        snippet = video["snippet"]

        statistics_data = video[
            "statistics"
        ]

        duration = video[
            "contentDetails"
        ][
            "duration"
        ]

        duration_seconds = (
            duration_to_seconds(
                duration
            )
        )

        title = snippet[
            "title"
        ]

        description = snippet.get(
            "description",
            ""
        )

        view_count = int(
            statistics_data.get(
                "viewCount",
                0
            )
        )

        published_at = snippet[
            "publishedAt"
        ]


        # ----------------------------
        # Shorts 1차 제외 기준
        #
        # 3분 이하 영상은 제외
        # ----------------------------

        if duration_seconds <= 180:
            continue


        long_videos.append(
            {
                "title": title,
                "views": view_count,
                "published_at": published_at,
                "duration_seconds": duration_seconds,
                "description": description
            }
        )


    # --------------------------------
    # 5. 최근 일반영상 10개
    # --------------------------------

    recent_videos = (
        long_videos[:10]
    )

    if not recent_videos:
        return None


    views = [
        video["views"]
        for video in recent_videos
    ]


    average_views = int(
        statistics.mean(
            views
        )
    )

    median_views = int(
        statistics.median(
            views
        )
    )


    # --------------------------------
    # 6. description 존재 비율
    # --------------------------------

    description_count = 0

    for video in recent_videos:

        description = (
            video[
                "description"
            ].strip()
        )

        if description:
            description_count += 1


    description_ratio = (
        description_count
        / len(recent_videos)
        * 100
    )


    # --------------------------------
    # 7. 결과
    # --------------------------------

    return {
        "channel_name": channel_name,
        "subscriber_count": subscriber_count,
        "average_views": average_views,
        "median_views": median_views,
        "description_ratio": description_ratio,
        "videos": recent_videos
    }


# --------------------------------
# 전체 크리에이터 분석
# --------------------------------

results = []

for creator_name, channel_id in creators.items():

    print()
    print("=" * 80)
    print(
        f"{creator_name} 분석 중..."
    )
    print("=" * 80)

    try:

        result = analyze_creator(
            channel_id
        )

        if not result:

            print(
                "분석 가능한 데이터가 없습니다."
            )

            continue


        result[
            "creator_name"
        ] = creator_name

        results.append(
            result
        )


        print(
            "실제 채널명:",
            result[
                "channel_name"
            ]
        )

        print(
            f"구독자 수: "
            f"{result['subscriber_count']:,}"
        )

        print(
            f"최근 10개 평균 조회수: "
            f"{result['average_views']:,}"
        )

        print(
            f"최근 10개 중앙값 조회수: "
            f"{result['median_views']:,}"
        )

        print(
            f"description 작성 비율: "
            f"{result['description_ratio']:.0f}%"
        )

        print()

        print(
            "최근 일반영상"
        )

        for i, video in enumerate(
            result[
                "videos"
            ],
            start=1
        ):

            print(
                f"{i}. "
                f"{video['title']}"
            )

            print(
                f"   조회수: "
                f"{video['views']:,}"
            )


    except Exception as e:

        print(
            f"오류 발생: {e}"
        )


# --------------------------------
# 최종 비교표
# --------------------------------

print()
print()
print("=" * 100)
print("크리에이터 비교")
print("=" * 100)

for result in results:

    print(
        f"{result['creator_name']} | "
        f"구독자 {result['subscriber_count']:,} | "
        f"평균 {result['average_views']:,} | "
        f"중앙값 {result['median_views']:,} | "
        f"description {result['description_ratio']:.0f}%"
    )