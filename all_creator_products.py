import os
import json
import requests

from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from openai import OpenAI


# =========================================================
# 환경변수
# =========================================================

load_dotenv()

youtube_api_key = os.getenv(
    "YOUTUBE_API_KEY"
)

openai_api_key = os.getenv(
    "OPENAI_API_KEY"
)


if not youtube_api_key:
    print(
        "❌ YOUTUBE_API_KEY를 찾을 수 없습니다."
    )
    raise SystemExit


if not openai_api_key:
    print(
        "❌ OPENAI_API_KEY를 찾을 수 없습니다."
    )
    raise SystemExit


client = OpenAI(
    api_key=openai_api_key
)


# =========================================================
# 기본 설정
# =========================================================

OUTPUT_FILE = (
    "all_product_results_60d.json"
)

ANALYSIS_DAYS = 60

MIN_VIDEO_SECONDS = 180


# =========================================================
# 크리에이터 목록
# =========================================================

creators = {

    # =====================================================
    # 국내 뷰티 전문 크리에이터
    # =====================================================

    "지냐": {
        "channel_id":
            "UCRiIf6rt91BVfZVtURRXlOw",

        "type":
            "beauty",

        "market":
            "KR"
    },


    "민스코": {
        "channel_id":
            "UCTQGAYPtbnCEfW9IGx65kiw",

        "type":
            "beauty",

        "market":
            "KR"
    },


    "아랑": {
        "channel_id":
            "UCY2YdDn7zXtRbNR0fJ9V_YQ",

        "type":
            "beauty",

        "market":
            "KR"
    },


    "유트루": {
        "channel_id":
            "UCH2mJnztSdNh8ADp2KmtUMQ",

        "type":
            "beauty",

        "market":
            "KR"
    },


    "레오제이": {
        "channel_id":
            "UCnFFOjljp1_sacTz7PfIIyg",

        "type":
            "beauty",

        "market":
            "KR"
    },


    "디렉터파이": {
        "channel_id":
            "UCqrNqg3UgVoD3Sa-F_TxuSA",

        "type":
            "beauty",

        "market":
            "KR"
    },


    "회사원A": {
        "channel_id":
            "UCnekLiljel-Px4ClMC7b3mg",

        "type":
            "beauty",

        "market":
            "KR"
    },


    # =====================================================
    # 국내 대중 인플루언서
    # =====================================================

    "프리지아": {
        "channel_id":
            "UCAbhooUR9thtUYAkLxk9iBg",

        "type":
            "mainstream",

        "market":
            "KR"
    },


    "성해은": {
        "channel_id":
            "UCI5ZLTYfIfXaeubb2ny0kNA",

        "type":
            "mainstream",

        "market":
            "KR"
    },


    "박지현": {
        "channel_id":
            "UC0JEvlaTw-nX7iDLb_L_ymA",

        "type":
            "mainstream",

        "market":
            "KR"
    },


    "민와와": {
        "channel_id":
            "UCJt-9Ku_D1Un6brccoTzglg",

        "type":
            "mainstream",

        "market":
            "KR"
    },


    "퀸승용": {
        "channel_id":
            "UCjqPJOm46V1pO_ffHoqrXow",

        "type":
            "mainstream",

        "market":
            "KR"
    },


    "박현지": {
        "channel_id":
            "UCmdOnmYKm4hijBxwGHtPT8Q",

        "type":
            "mainstream",

        "market":
            "KR"
    },


    "지연이라면": {
        "channel_id":
            "UCnwu3n--W9bbMsKQGyybKSQ",

        "type":
            "mainstream",

        "market":
            "KR"
    },


    "걍밍경": {
        "channel_id":
            "UCfqVrM2cvwxG3-EvxbsN0KQ",

        "type":
            "mainstream",

        "market":
            "KR"
    },


    # =====================================================
    # 해외 뷰티 크리에이터
    # =====================================================

    "James Welsh": {
        "channel_id":
            "UCPP291gN79qI1QZY1znOscg",

        "type":
            "global_beauty",

        "market":
            "GB"
    },


    "Gothamista": {
        "channel_id":
            "UC-X4BAoKxwGYIKrKfqk7yug",

        "type":
            "global_beauty",

        "market":
            "US"
    }

}


# =========================================================
# JSON 불러오기
# =========================================================

def load_json(
    filename,
    default=None
):

    if default is None:
        default = []


    if not os.path.exists(
        filename
    ):
        return default


    try:

        with open(
            filename,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)


    except Exception as e:

        print(
            f"⚠️ JSON 불러오기 오류: {e}"
        )

        return default


# =========================================================
# JSON 저장
# =========================================================

def save_results(
    results
):

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            results,
            f,
            ensure_ascii=False,
            indent=2
        )


# =========================================================
# 날짜 파싱
# =========================================================

def parse_youtube_date(
    date_string
):

    return datetime.fromisoformat(
        date_string.replace(
            "Z",
            "+00:00"
        )
    )


# =========================================================
# YouTube ISO 8601 duration → 초
# =========================================================

def duration_to_seconds(
    duration
):

    duration = duration.replace(
        "PT",
        ""
    )


    hours = 0
    minutes = 0
    seconds = 0


    if "H" in duration:

        parts = duration.split(
            "H"
        )

        hours = int(
            parts[0]
        )

        duration = parts[1]


    if "M" in duration:

        parts = duration.split(
            "M"
        )

        minutes = int(
            parts[0]
        )

        duration = parts[1]


    if "S" in duration:

        seconds_text = (
            duration.replace(
                "S",
                ""
            )
        )

        if seconds_text:

            seconds = int(
                seconds_text
            )


    return (
        hours * 3600
        + minutes * 60
        + seconds
    )


# =========================================================
# 기존 캐시 중 60일 이내 데이터만 유지
# =========================================================

def clean_old_cache(
    cached_results
):

    cutoff_date = (
        datetime.now(
            timezone.utc
        )
        - timedelta(
            days=ANALYSIS_DAYS
        )
    )


    cleaned = []


    for item in cached_results:

        published_at = item.get(
            "published_at"
        )


        if not published_at:
            continue


        try:

            published_date = (
                parse_youtube_date(
                    published_at
                )
            )


        except Exception:
            continue


        if published_date >= cutoff_date:

            cleaned.append(
                item
            )


    return cleaned


# =========================================================
# YouTube 채널 업로드 Playlist ID
# =========================================================

def get_uploads_playlist_id(
    channel_id
):

    url = (
        "https://www.googleapis.com/"
        "youtube/v3/channels"
    )


    params = {

        "part":
            "contentDetails",

        "id":
            channel_id,

        "key":
            youtube_api_key
    }


    response = requests.get(
        url,
        params=params,
        timeout=20
    )


    response.raise_for_status()


    data = response.json()


    if not data.get(
        "items"
    ):

        return None


    return (
        data[
            "items"
        ][0][
            "contentDetails"
        ][
            "relatedPlaylists"
        ][
            "uploads"
        ]
    )


# =========================================================
# 최근 업로드 video_id 가져오기
# =========================================================

def get_recent_video_ids(
    playlist_id
):

    url = (
        "https://www.googleapis.com/"
        "youtube/v3/playlistItems"
    )


    params = {

        "part":
            "contentDetails",

        "playlistId":
            playlist_id,

        "maxResults":
            50,

        "key":
            youtube_api_key
    }


    response = requests.get(
        url,
        params=params,
        timeout=20
    )


    response.raise_for_status()


    data = response.json()


    return [

        item[
            "contentDetails"
        ][
            "videoId"
        ]

        for item in data.get(
            "items",
            []
        )
    ]


# =========================================================
# 영상 상세정보
# =========================================================

def get_video_details(
    video_ids
):

    if not video_ids:
        return []


    url = (
        "https://www.googleapis.com/"
        "youtube/v3/videos"
    )


    params = {

        "part":
            "snippet,statistics,contentDetails",

        "id":
            ",".join(
                video_ids
            ),

        "key":
            youtube_api_key
    }


    response = requests.get(
        url,
        params=params,
        timeout=20
    )


    response.raise_for_status()


    data = response.json()


    return data.get(
        "items",
        []
    )


# =========================================================
# 최근 60일 일반 영상 가져오기
# =========================================================

def get_recent_videos(
    channel_id
):

    cutoff_date = (
        datetime.now(
            timezone.utc
        )
        - timedelta(
            days=ANALYSIS_DAYS
        )
    )


    playlist_id = (
        get_uploads_playlist_id(
            channel_id
        )
    )


    if not playlist_id:
        return []


    video_ids = (
        get_recent_video_ids(
            playlist_id
        )
    )


    if not video_ids:
        return []


    video_details = (
        get_video_details(
            video_ids
        )
    )


    videos = []


    for video in video_details:

        snippet = video.get(
            "snippet",
            {}
        )

        content_details = video.get(
            "contentDetails",
            {}
        )

        statistics = video.get(
            "statistics",
            {}
        )


        published_at = snippet.get(
            "publishedAt"
        )


        if not published_at:
            continue


        try:

            published_date = (
                parse_youtube_date(
                    published_at
                )
            )


        except Exception:
            continue


        # -------------------------------------------------
        # 60일 이전 제외
        # -------------------------------------------------

        if published_date < cutoff_date:
            continue


        duration = (
            content_details.get(
                "duration",
                ""
            )
        )


        duration_seconds = (
            duration_to_seconds(
                duration
            )
        )


        # -------------------------------------------------
        # 3분 이하 영상 제외
        # -------------------------------------------------

        if (
            duration_seconds
            <= MIN_VIDEO_SECONDS
        ):
            continue


        videos.append(
            {

                "video_id":
                    video.get(
                        "id",
                        ""
                    ),

                "title":
                    snippet.get(
                        "title",
                        ""
                    ),

                "description":
                    snippet.get(
                        "description",
                        ""
                    ),

                "published_at":
                    published_at,

                "views":
                    int(
                        statistics.get(
                            "viewCount",
                            0
                        )
                    ),

                "duration_seconds":
                    duration_seconds
            }
        )


    videos = sorted(

        videos,

        key=lambda x: x[
            "published_at"
        ],

        reverse=True
    )


    return videos


# =========================================================
# OpenAI 제품 추출
# =========================================================

def extract_products_with_ai(
    video
):

    prompt = f"""
당신은 뷰티 산업 데이터 분석을 위한 정보 추출 AI입니다.

아래 YouTube 영상의 제목과 description을 읽고
실제로 언급되거나 사용되거나 추천된
뷰티 관련 브랜드와 제품을 추출하세요.

영상의 언어는 한국어일 수도 있고
영어 또는 다른 언어일 수도 있습니다.

브랜드와 제품명은 가능한 경우
공식 브랜드명과 공식 제품명을 유지하세요.

description에 없는 정보를 추측하지 마세요.


출력은 반드시 JSON만 사용하세요.

구조:

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


category:

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


exposure_type:

- 추천
- 사용
- 신제품소개
- 언박싱
- 공동개발
- 광고
- 단순언급
- 기타


commercial_relation:

- 직접구매
- 제품제공
- 단순선물
- 유료광고
- 공동개발
- 노출의무없음
- 불명확


규칙:

1.
description에 없는 브랜드나 제품을
추측하지 마세요.

2.
패션, 음식, 여행, 웨딩 업체 등
뷰티와 무관한 항목은 제외하세요.

3.
동일 제품은 한 번만 추출하세요.

4.
제품명이 명확하지 않으면
억지로 생성하지 마세요.

5.
광고 여부를 추측하지 마세요.

6.
제품제공, 직접구매 등의 관계도
description에 근거가 있을 때만 판단하세요.

7.
영문 브랜드명은 임의로 한국어 브랜드명으로
번역하지 마세요.

8.
한국 브랜드의 영문 표기가 사용된 경우
가능하면 일반적으로 사용하는 브랜드명으로 정리하세요.

9.
뷰티 제품이 없다면:

{{
    "beauty_related": false,
    "products": []
}}

로 반환하세요.


영상 제목:

{video["title"]}


영상 description:

{video["description"]}
"""


    response = (
        client.responses.create(

            model="gpt-5.6-luna",

            input=prompt
        )
    )


    text = (
        response.output_text
        .strip()
    )


    # -----------------------------------------------------
    # 코드블록 제거
    # -----------------------------------------------------

    if text.startswith(
        "```json"
    ):

        text = text[
            len("```json"):
        ]


    elif text.startswith(
        "```"
    ):

        text = text[
            len("```"):
        ]


    if text.endswith(
        "```"
    ):

        text = text[:-3]


    text = text.strip()


    return json.loads(
        text
    )


# =========================================================
# 기존 캐시 불러오기
# =========================================================

cached_results = load_json(
    OUTPUT_FILE
)


# =========================================================
# 오래된 캐시 제거
# =========================================================

cached_results = clean_old_cache(
    cached_results
)


# =========================================================
# video_id 기준 캐시 Dictionary
# =========================================================

cache_by_video_id = {}


for item in cached_results:

    video_id = item.get(
        "video_id"
    )


    if video_id:

        cache_by_video_id[
            video_id
        ] = item


# =========================================================
# 시작 메시지
# =========================================================

print()
print("=" * 110)

print(
    "💄 BeautyAlpha YouTube Creator Update"
)

print("=" * 110)

print(
    f"등록 크리에이터: "
    f"{len(creators)}명"
)

print(
    f"기존 60일 캐시 영상: "
    f"{len(cache_by_video_id)}개"
)


# =========================================================
# 실행 결과
# =========================================================

final_results = []

added_video_ids = set()


new_video_count = 0

cached_video_count = 0

error_count = 0


# =========================================================
# 전체 크리에이터 실행
# =========================================================

for creator_index, (
    creator_name,
    info
) in enumerate(
    creators.items(),
    start=1
):


    creator_type = info.get(
        "type",
        ""
    )


    market = info.get(
        "market",
        "KR"
    )


    print()
    print("=" * 110)


    print(
        f"[{creator_index}/{len(creators)}] "
        f"{creator_name} "
        f"| {creator_type} "
        f"| {market}"
    )


    print("=" * 110)


    # =====================================================
    # YouTube 영상 가져오기
    # =====================================================

    try:

        videos = (
            get_recent_videos(
                info[
                    "channel_id"
                ]
            )
        )


    except Exception as e:

        print(
            f"❌ YouTube 조회 오류: {e}"
        )

        error_count += 1

        continue


    print(
        f"최근 {ANALYSIS_DAYS}일 "
        f"일반영상: "
        f"{len(videos)}개"
    )


    # =====================================================
    # 영상별 처리
    # =====================================================

    for video_index, video in enumerate(
        videos,
        start=1
    ):


        video_id = (
            video[
                "video_id"
            ]
        )


        # -------------------------------------------------
        # 중복 방지
        # -------------------------------------------------

        if video_id in added_video_ids:

            continue


        # =================================================
        # 기존 캐시 재사용
        # =================================================

        if video_id in cache_by_video_id:


            cached_item = (
                cache_by_video_id[
                    video_id
                ].copy()
            )


            # ---------------------------------------------
            # 바뀔 수 있는 YouTube 정보 최신화
            # ---------------------------------------------

            cached_item[
                "views"
            ] = video[
                "views"
            ]


            cached_item[
                "title"
            ] = video[
                "title"
            ]


            cached_item[
                "published_at"
            ] = video[
                "published_at"
            ]


            cached_item[
                "creator"
            ] = creator_name


            cached_item[
                "creator_type"
            ] = creator_type


            # =============================================
            # 시장 정보 추가 / 최신화
            # =============================================

            cached_item[
                "market"
            ] = market


            final_results.append(
                cached_item
            )


            added_video_ids.add(
                video_id
            )


            cached_video_count += 1


            print(
                f"[{video_index}/{len(videos)}] "
                f"♻️ 캐시 사용 | "
                f"{video['title']}"
            )


            continue


        # =================================================
        # 신규 영상
        # =================================================

        print()
        print(
            f"[{video_index}/{len(videos)}] "
            f"🆕 신규 영상"
        )

        print(
            video[
                "title"
            ]
        )

        print(
            f"시장: {market}"
        )

        print(
            f"업로드: "
            f"{video['published_at']}"
        )

        print(
            "AI 제품 추출 중..."
        )


        try:

            extracted = (
                extract_products_with_ai(
                    video
                )
            )


            result = {

                "creator":
                    creator_name,

                "creator_type":
                    creator_type,

                "market":
                    market,

                "video_id":
                    video[
                        "video_id"
                    ],

                "title":
                    video[
                        "title"
                    ],

                "published_at":
                    video[
                        "published_at"
                    ],

                "views":
                    video[
                        "views"
                    ],

                "beauty_related":
                    extracted.get(
                        "beauty_related",
                        False
                    ),

                "products":
                    extracted.get(
                        "products",
                        []
                    )
            }


            final_results.append(
                result
            )


            added_video_ids.add(
                video_id
            )


            new_video_count += 1


            print(
                f"✅ 제품 "
                f"{len(result['products'])}개 추출"
            )


            # ---------------------------------------------
            # 신규 영상 하나 끝날 때마다 저장
            # ---------------------------------------------

            save_results(
                final_results
            )


        except Exception as e:

            print(
                f"❌ AI 분석 오류: {e}"
            )

            error_count += 1


# =========================================================
# 최신순 정렬
# =========================================================

final_results = sorted(

    final_results,

    key=lambda x: x.get(
        "published_at",
        ""
    ),

    reverse=True
)


# =========================================================
# 최종 저장
# =========================================================

save_results(
    final_results
)


# =========================================================
# 국가별 영상 개수 확인
# =========================================================

market_counts = {}


for item in final_results:

    market = item.get(
        "market",
        "KR"
    )

    market_counts[
        market
    ] = (
        market_counts.get(
            market,
            0
        )
        + 1
    )


# =========================================================
# 완료
# =========================================================

print()
print("=" * 110)

print(
    "✅ BeautyAlpha YouTube 업데이트 완료"
)

print("=" * 110)


print(
    f"♻️ 기존 분석 재사용: "
    f"{cached_video_count}개"
)


print(
    f"🆕 새로 AI 분석: "
    f"{new_video_count}개"
)


print(
    f"❌ 오류: "
    f"{error_count}개"
)


print(
    f"📦 최종 60일 영상: "
    f"{len(final_results)}개"
)


print()
print(
    "🌍 시장별 영상 수"
)


for market, count in sorted(
    market_counts.items()
):

    print(
        f"• {market}: "
        f"{count}개"
    )


print()
print(
    f"💾 저장 파일: "
    f"{OUTPUT_FILE}"
)


if new_video_count == 0:

    print()
    print(
        "새로운 영상이 없어 "
        "OpenAI 제품 추출 호출을 하지 않았습니다."
    )