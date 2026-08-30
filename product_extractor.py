import os
import json
import requests
from dotenv import load_dotenv
from openai import OpenAI


# =========================================================
# 환경변수 불러오기
# =========================================================

load_dotenv()

youtube_api_key = os.getenv("YOUTUBE_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

if not youtube_api_key:
    print("YouTube API 키를 찾을 수 없습니다.")
    exit()

if not openai_api_key:
    print("OpenAI API 키를 찾을 수 없습니다.")
    exit()


client = OpenAI(
    api_key=openai_api_key
)


# =========================================================
# 테스트 채널
# 지냐 Jinyaa
# =========================================================

channel_id = "UCRiIf6rt91BVfZVtURRXlOw"


# =========================================================
# ISO 8601 길이를 초로 변환
# 예: PT32M33S → 1953초
# =========================================================

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
        seconds = int(
            duration.replace("S", "")
        )

    return (
        hours * 3600
        + minutes * 60
        + seconds
    )


# =========================================================
# YouTube 최근 일반영상 가져오기
# =========================================================

def get_recent_videos(channel_id, count=3):

    # -----------------------------------------------------
    # 1. 채널의 업로드 플레이리스트 ID 찾기
    # -----------------------------------------------------

    channel_url = (
        "https://www.googleapis.com/youtube/v3/channels"
    )

    channel_params = {
        "part": "contentDetails",
        "id": channel_id,
        "key": youtube_api_key
    }

    response = requests.get(
        channel_url,
        params=channel_params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    uploads_playlist_id = (
        data["items"][0]
        ["contentDetails"]
        ["relatedPlaylists"]
        ["uploads"]
    )


    # -----------------------------------------------------
    # 2. 최근 업로드 50개
    # -----------------------------------------------------

    playlist_url = (
        "https://www.googleapis.com/youtube/v3/playlistItems"
    )

    playlist_params = {
        "part": "contentDetails",
        "playlistId": uploads_playlist_id,
        "maxResults": 50,
        "key": youtube_api_key
    }

    response = requests.get(
        playlist_url,
        params=playlist_params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    video_ids = [
        item["contentDetails"]["videoId"]
        for item in data.get("items", [])
    ]


    # -----------------------------------------------------
    # 3. 영상 상세정보
    # -----------------------------------------------------

    videos_url = (
        "https://www.googleapis.com/youtube/v3/videos"
    )

    videos_params = {
        "part": "snippet,statistics,contentDetails",
        "id": ",".join(video_ids),
        "key": youtube_api_key
    }

    response = requests.get(
        videos_url,
        params=videos_params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()


    # -----------------------------------------------------
    # 4. 3분 이하 영상 제외
    # -----------------------------------------------------

    videos = []

    for video in data.get("items", []):

        duration = (
            video["contentDetails"]["duration"]
        )

        duration_seconds = (
            duration_to_seconds(duration)
        )

        if duration_seconds <= 180:
            continue

        snippet = video["snippet"]

        videos.append(
            {
                "video_id": video["id"],

                "title": snippet["title"],

                "description": snippet.get(
                    "description",
                    ""
                ),

                "published_at": snippet[
                    "publishedAt"
                ],

                "views": int(
                    video["statistics"].get(
                        "viewCount",
                        0
                    )
                )
            }
        )

        if len(videos) >= count:
            break


    return videos


# =========================================================
# OpenAI로 제품 추출
# =========================================================

def extract_products_with_ai(video):

    prompt = f"""
당신은 뷰티 산업 데이터 분석을 위한 정보 추출 AI입니다.

아래 YouTube 영상의 제목과 description을 읽고,
영상에서 실제로 언급되거나 사용되거나 추천된
뷰티 관련 브랜드와 제품을 추출하세요.

목적은 향후
'어떤 뷰티 브랜드가 크리에이터들에게 자주 언급되는지'
분석하는 것입니다.

반드시 JSON만 출력하세요.


출력 구조:

{{
  "beauty_related": true,
  "products": [
    {{
      "brand": "",
      "product": "",
      "category": "",
      "exposure_type": "",
      "commercial_relation": ""
    }}
  ]
}}


[brand]

브랜드 이름을 작성하세요.

예:
- 이니스프리
- 에뛰드
- 넘버즈인
- 메디힐
- 페리페라


[product]

제품명을 작성하세요.

색상이나 호수는 제품을 구분하는 데 필요한 경우 포함해도 됩니다.


[category]

아래 중 가장 적절한 하나만 사용하세요.

- 스킨케어
- 클렌징
- 선케어
- 베이스메이크업
- 아이메이크업
- 립
- 블러셔
- 하이라이터
- 쉐딩
- 브로우
- 마스카라
- 뷰티도구
- 헤어
- 바디
- 이너뷰티
- 기타


[exposure_type]

영상에서 해당 제품이 어떤 방식으로 등장했는지 아래 중 하나로 작성하세요.

- 추천
- 사용
- 신제품소개
- 언박싱
- 공동개발
- 광고
- 단순언급
- 기타


[commercial_relation]

description에 적힌 정보만 근거로 아래 중 하나를 사용하세요.

- 직접구매
- 제품제공
- 단순선물
- 유료광고
- 공동개발
- 노출의무없음
- 불명확


중요 규칙:

1. description에 없는 정보를 추측하지 마세요.

2. 패션, 음식, 웨딩업체 등 뷰티와 관계없는 항목은 제외하세요.

3. 화장품, 스킨케어, 뷰티도구, 헤어, 바디 제품은 포함 가능합니다.

4. 동일 제품이 여러 번 등장하면 하나만 추출하세요.

5. 제품명이 명확하지 않은 경우 억지로 만들지 마세요.

6. 브랜드만 있고 제품명이 전혀 확인되지 않으면
product에는 빈 문자열을 사용할 수 있습니다.

7. 광고 여부를 임의로 판단하지 마세요.

8. 영상 전체가 뷰티와 사실상 무관하고
뷰티 제품 정보가 없다면:

"beauty_related": false

그리고 products는 빈 배열로 출력하세요.

9. JSON 외의 설명은 절대 출력하지 마세요.


영상 제목:

{video["title"]}


영상 description:

{video["description"]}
"""


    response = client.responses.create(
        model="gpt-5.6-luna",
        input=prompt
    )

    result_text = response.output_text

    return json.loads(result_text)


# =========================================================
# 실행
# =========================================================

videos = get_recent_videos(
    channel_id,
    count=3
)


all_results = []


for i, video in enumerate(
    videos,
    start=1
):

    print()
    print("=" * 100)
    print(f"영상 {i}")
    print("=" * 100)

    print("제목:")
    print(video["title"])

    print(
        f"조회수: {video['views']:,}"
    )

    print()

    print(
        "AI가 제품 정보를 추출하고 있습니다..."
    )


    try:

        extracted = (
            extract_products_with_ai(
                video
            )
        )

    except json.JSONDecodeError:

        print(
            "AI 결과를 JSON으로 변환하지 못했습니다."
        )

        continue

    except Exception as e:

        print(
            f"오류 발생: {e}"
        )

        continue


    result = {
        "video_id": video[
            "video_id"
        ],

        "title": video[
            "title"
        ],

        "published_at": video[
            "published_at"
        ],

        "views": video[
            "views"
        ],

        "beauty_related": extracted.get(
            "beauty_related",
            False
        ),

        "products": extracted.get(
            "products",
            []
        )
    }


    all_results.append(
        result
    )


    print()

    if not result[
        "beauty_related"
    ]:

        print(
            "→ 뷰티 제품 정보가 없는 영상"
        )

        continue


    products = result[
        "products"
    ]


    print(
        f"추출된 제품 수: "
        f"{len(products)}"
    )

    print()


    for product in products:

        print(
            f"브랜드: "
            f"{product.get('brand', '')}"
        )

        print(
            f"제품: "
            f"{product.get('product', '')}"
        )

        print(
            f"카테고리: "
            f"{product.get('category', '')}"
        )

        print(
            f"노출 방식: "
            f"{product.get('exposure_type', '')}"
        )

        print(
            f"관계: "
            f"{product.get('commercial_relation', '')}"
        )

        print("-" * 60)


# =========================================================
# JSON 파일 저장
# =========================================================

output_file = "product_results.json"

with open(
    output_file,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        all_results,
        f,
        ensure_ascii=False,
        indent=2
    )


print()
print("=" * 100)

print(
    f"완료! 결과가 "
    f"{output_file} 파일에 저장되었습니다."
)