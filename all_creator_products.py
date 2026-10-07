import os
import json
import requests

from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from openai import OpenAI


# =========================================================
# 기본 설정
# =========================================================

CREATOR_FILE = "creators.json"
OUTPUT_FILE = "all_product_results_60d.json"

ANALYSIS_DAYS = 60
MIN_VIDEO_SECONDS = 180


# =========================================================
# 환경변수 / Streamlit Secrets
# =========================================================

load_dotenv()


def get_secret(name):

    # 로컬 .env / 환경변수
    value = os.getenv(name)

    if value:
        return value

    # Streamlit Cloud
    try:

        import streamlit as st

        value = st.secrets.get(
            name
        )

        if value:
            return value

    except Exception:
        pass

    return None


youtube_api_key = get_secret(
    "YOUTUBE_API_KEY"
)

openai_api_key = get_secret(
    "OPENAI_API_KEY"
)


if not youtube_api_key:

    print(
        "YOUTUBE_API_KEY를 찾을 수 없습니다."
    )

    raise SystemExit


if not openai_api_key:

    print(
        "OPENAI_API_KEY를 찾을 수 없습니다."
    )

    raise SystemExit


client = OpenAI(
    api_key=openai_api_key
)


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
            f"JSON 읽기 오류: {filename} / {e}"
        )

        return default


# =========================================================
# JSON 저장
# =========================================================

def save_json(
    filename,
    data
):

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )


# =========================================================
# 크리에이터 불러오기
# =========================================================

def load_creators():

    creator_list = load_json(
        CREATOR_FILE
    )

    active_creators = []


    for creator in creator_list:

        if not isinstance(
            creator,
            dict
        ):
            continue


        if not creator.get(
            "active",
            True
        ):
            continue


        name = str(
            creator.get(
                "name",
                ""
            )
        ).strip()


        channel_id = str(
            creator.get(
                "channel_id",
                ""
            )
        ).strip()


        creator_type = str(
            creator.get(
                "creator_type",
                ""
            )
        ).strip()


        market = str(
            creator.get(
                "market",
                ""
            )
        ).strip()


        if not name:
            continue


        if not channel_id:
            continue


        active_creators.append(
            {
                "name":
                    name,

                "channel_id":
                    channel_id,

                "creator_type":
                    creator_type,

                "market":
                    market
            }
        )


    return active_creators


# =========================================================
# YouTube 날짜 파싱
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
# ISO 8601 영상 길이 → 초
# =========================================================

def duration_to_seconds(
    duration
):

    if not duration:
        return 0


    duration = duration.replace(
        "PT",
        ""
    )


    hours = 0
    minutes = 0
    seconds = 0


    if "H" in duration:

        parts = duration.split(
            "H",
            1
        )

        try:

            hours = int(
                parts[0]
            )

        except Exception:

            hours = 0


        duration = parts[1]


    if "M" in duration:

        parts = duration.split(
            "M",
            1
        )

        try:

            minutes = int(
                parts[0]
            )

        except Exception:

            minutes = 0


        duration = parts[1]


    if "S" in duration:

        seconds_text = duration.replace(
            "S",
            ""
        )


        try:

            seconds = int(
                seconds_text
            )

        except Exception:

            seconds = 0


    return (
        hours * 3600
        + minutes * 60
        + seconds
    )


# =========================================================
# 기존 캐시에서 60일 지난 결과 제거
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

        if not isinstance(
            item,
            dict
        ):
            continue


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
# 업로드 Playlist ID 조회
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


    items = data.get(
        "items",
        []
    )


    if not items:

        return None


    try:

        return (
            items[0]
            ["contentDetails"]
            ["relatedPlaylists"]
            ["uploads"]
        )

    except Exception:

        return None


# =========================================================
# 업로드 영상 ID
#
# 현재 버전은 최신 50개
# 다음 단계에서 pagination 추가 예정
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


    video_ids = []


    for item in data.get(
        "items",
        []
    ):

        try:

            video_id = (
                item[
                    "contentDetails"
                ][
                    "videoId"
                ]
            )

        except Exception:

            continue


        if video_id:

            video_ids.append(
                video_id
            )


    return video_ids


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


    details = (
        get_video_details(
            video_ids
        )
    )


    videos = []


    for video in details:

        snippet = video.get(
            "snippet",
            {}
        )

        statistics = video.get(
            "statistics",
            {}
        )

        content_details = video.get(
            "contentDetails",
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


        # 60일 이전 제외
        if published_date < cutoff_date:
            continue


        duration = content_details.get(
            "duration",
            ""
        )


        duration_seconds = (
            duration_to_seconds(
                duration
            )
        )


        # 현재는 3분 이하 제외
        if (
            duration_seconds
            <= MIN_VIDEO_SECONDS
        ):

            continue


        try:

            views = int(
                statistics.get(
                    "viewCount",
                    0
                )
            )

        except Exception:

            views = 0


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
                    views,

                "duration_seconds":
                    duration_seconds
            }
        )


    videos = sorted(
        videos,
        key=lambda x: x.get(
            "published_at",
            ""
        ),
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
당신은 뷰티 산업 데이터 분석용 정보 추출 AI입니다.

아래 YouTube 영상의 제목과 description을 읽고
실제로 언급되거나 사용되거나 추천된
뷰티 관련 브랜드와 제품을 추출하세요.

영상의 언어는 한국어, 영어, 일본어 등
여러 언어일 수 있습니다.

description에 없는 정보를 추측하지 마세요.

반드시 JSON만 출력하세요.


출력 형식:

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
description에 없는 브랜드 또는 제품을
추측하지 마세요.

2.
패션, 음식, 여행, 웨딩 등
뷰티와 무관한 항목은 제외하세요.

3.
동일 제품은 한 번만 추출하세요.

4.
제품명이 불명확하면
억지로 생성하지 마세요.

5.
광고 여부를 추측하지 마세요.

6.
제품제공·직접구매·유료광고 등도
description에서 근거가 있을 때만 판단하세요.

7.
영문 브랜드명은 임의로 한글 번역하지 마세요.

8.
한국 브랜드의 공식 영문명이 사용된 경우
일반적으로 사용하는 브랜드명으로 정리할 수 있습니다.

9.
뷰티 제품이 없다면 아래처럼 반환하세요.

{{
    "beauty_related": false,
    "products": []
}}


영상 제목:

{video["title"]}


영상 description:

{video["description"]}
"""


    response = client.responses.create(
        model="gpt-5.6-luna",
        input=prompt
    )


    text = (
        response.output_text
        .strip()
    )


    # 코드블록 제거
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
# MAIN
# =========================================================

def main():

    creators = load_creators()


    print()
    print("=" * 110)

    print(
        "BeautyAlpha YouTube Creator Update"
    )

    print("=" * 110)

    print(
        f"활성 크리에이터: "
        f"{len(creators)}명"
    )


    # =====================================================
    # 기존 캐시
    # =====================================================

    cached_results = load_json(
        OUTPUT_FILE
    )


    cached_results = clean_old_cache(
        cached_results
    )


    cache_by_video_id = {}


    for item in cached_results:

        if not isinstance(
            item,
            dict
        ):
            continue


        video_id = item.get(
            "video_id"
        )


        if video_id:

            cache_by_video_id[
                video_id
            ] = item


    print(
        f"기존 60일 캐시 영상: "
        f"{len(cache_by_video_id)}개"
    )


    # =====================================================
    # 결과 컨테이너
    # =====================================================

    final_results = []

    added_video_ids = set()

    new_video_count = 0
    cached_video_count = 0
    error_count = 0


    # =====================================================
    # 크리에이터별 실행
    # =====================================================

    for creator_index, info in enumerate(
        creators,
        start=1
    ):

        creator_name = info.get(
            "name",
            ""
        )

        channel_id = info.get(
            "channel_id",
            ""
        )

        creator_type = info.get(
            "creator_type",
            ""
        )

        market = info.get(
            "market",
            ""
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


        # =================================================
        # YouTube 영상 조회
        # =================================================

        try:

            videos = get_recent_videos(
                channel_id
            )

        except Exception as e:

            print(
                f"YouTube 조회 오류: {e}"
            )

            error_count += 1

            continue


        print(
            f"최근 {ANALYSIS_DAYS}일 "
            f"일반영상: "
            f"{len(videos)}개"
        )


        # =================================================
        # 영상별 처리
        # =================================================

        for video_index, video in enumerate(
            videos,
            start=1
        ):

            video_id = video.get(
                "video_id",
                ""
            )


            if not video_id:
                continue


            if video_id in added_video_ids:
                continue


            # =============================================
            # 기존 캐시 재사용
            # =============================================

            if video_id in cache_by_video_id:

                cached_item = (
                    cache_by_video_id[
                        video_id
                    ].copy()
                )


                # 최신 정보 갱신
                cached_item[
                    "views"
                ] = video.get(
                    "views",
                    0
                )


                cached_item[
                    "title"
                ] = video.get(
                    "title",
                    ""
                )


                cached_item[
                    "published_at"
                ] = video.get(
                    "published_at",
                    ""
                )


                cached_item[
                    "creator"
                ] = creator_name


                cached_item[
                    "creator_type"
                ] = creator_type


                cached_item[
                    "market"
                ] = market


                cached_item[
                    "duration_seconds"
                ] = video.get(
                    "duration_seconds",
                    0
                )


                final_results.append(
                    cached_item
                )


                added_video_ids.add(
                    video_id
                )


                cached_video_count += 1


                print(
                    f"[{video_index}/{len(videos)}] "
                    f"캐시 사용 | "
                    f"{video.get('title', '')}"
                )


                continue


            # =============================================
            # 신규 영상 AI 분석
            # =============================================

            print()
            print(
                f"[{video_index}/{len(videos)}] "
                f"신규 영상"
            )

            print(
                video.get(
                    "title",
                    ""
                )
            )

            print(
                f"시장: {market}"
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
                        video_id,

                    "title":
                        video.get(
                            "title",
                            ""
                        ),

                    "published_at":
                        video.get(
                            "published_at",
                            ""
                        ),

                    "views":
                        video.get(
                            "views",
                            0
                        ),

                    "duration_seconds":
                        video.get(
                            "duration_seconds",
                            0
                        ),

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
                    f"제품 "
                    f"{len(result['products'])}개 추출"
                )


                # -----------------------------------------
                # 중간 저장
                # -----------------------------------------

                save_json(
                    OUTPUT_FILE,
                    final_results
                )


            except Exception as e:

                print(
                    f"AI 분석 오류: {e}"
                )

                error_count += 1


    # =====================================================
    # 최신순 정렬
    # =====================================================

    final_results = sorted(
        final_results,
        key=lambda x: x.get(
            "published_at",
            ""
        ),
        reverse=True
    )


    # =====================================================
    # 최종 저장
    # =====================================================

    save_json(
        OUTPUT_FILE,
        final_results
    )


    # =====================================================
    # 시장별 영상 수
    # =====================================================

    market_counts = {}


    for item in final_results:

        market = item.get(
            "market",
            "UNKNOWN"
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


    # =====================================================
    # 크리에이터 유형별 영상 수
    # =====================================================

    creator_type_counts = {}


    for item in final_results:

        creator_type = item.get(
            "creator_type",
            "UNKNOWN"
        )


        creator_type_counts[
            creator_type
        ] = (
            creator_type_counts.get(
                creator_type,
                0
            )
            + 1
        )


    # =====================================================
    # 완료
    # =====================================================

    print()
    print("=" * 110)

    print(
        "BeautyAlpha YouTube 업데이트 완료"
    )

    print("=" * 110)


    print(
        f"기존 분석 재사용: "
        f"{cached_video_count}개"
    )


    print(
        f"새로 AI 분석: "
        f"{new_video_count}개"
    )


    print(
        f"오류: "
        f"{error_count}개"
    )


    print(
        f"최종 60일 영상: "
        f"{len(final_results)}개"
    )


    print()
    print(
        "[시장별 영상 수]"
    )


    for market, count in sorted(
        market_counts.items()
    ):

        print(
            f"{market}: "
            f"{count}개"
        )


    print()
    print(
        "[크리에이터 유형별 영상 수]"
    )


    for creator_type, count in sorted(
        creator_type_counts.items()
    ):

        print(
            f"{creator_type}: "
            f"{count}개"
        )


    print()
    print(
        f"저장 파일: "
        f"{OUTPUT_FILE}"
    )


    if new_video_count == 0:

        print()
        print(
            "새로운 영상이 없어 "
            "OpenAI 제품 추출 호출을 하지 않았습니다."
        )


# =========================================================
# 실행
# =========================================================

if __name__ == "__main__":

    main()