from pytrends.request import TrendReq
import json
import time


# =========================================================
# BeautyAlpha TOP 10 불러오기
# =========================================================

with open(
    "beauty_alpha_top10.json",
    "r",
    encoding="utf-8"
) as f:

    top10 = json.load(f)


# =========================================================
# 브랜드 다국어 사전
#
# 중요:
# 중국어 표기는 공식/현지 사용명을 확인한 것만
# 나중에 추가하는 것을 권장
# =========================================================

BRAND_ALIASES = {

    "닥터엘시아": {
        "ko": [
            "닥터엘시아"
        ],

        "en": [
            "Dr. Althea",
            "Dr Althea"
        ],

        "ja": [
            "ドクターエルシア",
            "Dr. Althea"
        ],

        "zh": [
            "Dr. Althea"
        ]
    },


    "토르홉": {
        "ko": [
            "토르홉"
        ],

        "en": [
            "Thorhop",
            "THORHOP"
        ],

        "ja": [
            "トールホップ",
            "THORHOP"
        ],

        "zh": [
            "THORHOP"
        ]
    },


    "웨이크메이크": {
        "ko": [
            "웨이크메이크"
        ],

        "en": [
            "WAKEMAKE",
            "WakeMake"
        ],

        "ja": [
            "ウェイクメイク",
            "WAKEMAKE"
        ],

        "zh": [
            "WAKEMAKE"
        ]
    },


    "이니스프리": {
        "ko": [
            "이니스프리"
        ],

        "en": [
            "innisfree",
            "Innisfree"
        ],

        "ja": [
            "イニスフリー",
            "innisfree"
        ],

        "zh": [
            "innisfree"
        ]
    },


    "입큰": {
        "ko": [
            "입큰"
        ],

        "en": [
            "IPKN",
            "Ipkn"
        ],

        "ja": [
            "IPKN",
            "イプクン"
        ],

        "zh": [
            "IPKN"
        ]
    },


    "라네즈": {
        "ko": [
            "라네즈"
        ],

        "en": [
            "LANEIGE",
            "Laneige"
        ],

        "ja": [
            "ラネージュ",
            "LANEIGE"
        ],

        "zh": [
            "LANEIGE"
        ]
    },


    "에뛰드": {
        "ko": [
            "에뛰드"
        ],

        "en": [
            "ETUDE",
            "Etude"
        ],

        "ja": [
            "エチュード",
            "ETUDE"
        ],

        "zh": [
            "ETUDE"
        ]
    },


    "스튜디오17": {
        "ko": [
            "스튜디오17"
        ],

        "en": [
            "Studio17",
            "STUDIO17"
        ],

        "ja": [
            "STUDIO17"
        ],

        "zh": [
            "STUDIO17"
        ]
    },


    "어바웃톤": {
        "ko": [
            "어바웃톤"
        ],

        "en": [
            "About Tone",
            "ABOUT TONE",
            "About_Tone"
        ],

        "ja": [
            "アバウトトーン",
            "ABOUT TONE"
        ],

        "zh": [
            "ABOUT TONE"
        ]
    },


    "일리윤": {
        "ko": [
            "일리윤"
        ],

        "en": [
            "ILLIYOON",
            "Illiyoon"
        ],

        "ja": [
            "イリユン",
            "ILLIYOON"
        ],

        "zh": [
            "ILLIYOON"
        ]
    }
}


# =========================================================
# 분석 국가
# =========================================================

REGIONS = {

    "KR": {
        "name": "한국",
        "languages": [
            "ko",
            "en"
        ]
    },

    "US": {
        "name": "미국",
        "languages": [
            "en"
        ]
    },

    "JP": {
        "name": "일본",
        "languages": [
            "ja",
            "en"
        ]
    },

    "TW": {
        "name": "대만",
        "languages": [
            "zh",
            "en"
        ]
    },

    "HK": {
        "name": "홍콩",
        "languages": [
            "zh",
            "en"
        ]
    }
}


# =========================================================
# Google Trends 연결
# =========================================================

pytrends = TrendReq(
    hl="ko-KR",
    tz=-540
)


# =========================================================
# 검색어 그룹 생성
#
# 예:
#
# 닥터엘시아 + Dr. Althea + Dr Althea
#
# Google Trends에서 "+"는 여러 표현을
# 하나의 검색 그룹으로 묶는 용도로 사용
# =========================================================

def make_search_group(
    brand,
    languages
):

    aliases = BRAND_ALIASES.get(
        brand,
        {}
    )

    terms = []


    for language in languages:

        language_terms = aliases.get(
            language,
            []
        )

        terms.extend(
            language_terms
        )


    # 등록되지 않은 브랜드라면
    # 원래 브랜드명을 최소 검색어로 사용
    if not terms:

        terms = [
            brand
        ]


    # 중복 제거
    unique_terms = []

    for term in terms:

        if term not in unique_terms:

            unique_terms.append(
                term
            )


    return " + ".join(
        unique_terms
    )


# =========================================================
# Trends 데이터 분석
# =========================================================

def analyze_region(
    brand,
    geo,
    languages
):

    search_group = make_search_group(
        brand,
        languages
    )


    print(
        f"검색 그룹: {search_group}"
    )


    pytrends.build_payload(
        kw_list=[
            search_group
        ],
        cat=0,
        timeframe="today 3-m",
        geo=geo,
        gprop=""
    )


    trend_data = (
        pytrends.interest_over_time()
    )


    if trend_data.empty:

        return {
            "available": False,

            "search_group":
                search_group
        }


    if "isPartial" in trend_data.columns:

        trend_data = trend_data.drop(
            columns=[
                "isPartial"
            ]
        )


    column_name = (
        trend_data.columns[0]
    )


    values = (
        trend_data[
            column_name
        ]
        .tolist()
    )


    # =====================================================
    # 최근 30일
    # =====================================================

    recent_values = (
        values[-30:]
    )


    # =====================================================
    # 이전 30일
    # =====================================================

    previous_values = (
        values[-60:-30]
    )


    # =====================================================
    # 평균
    # =====================================================

    if recent_values:

        recent_avg = (
            sum(recent_values)
            / len(recent_values)
        )

    else:

        recent_avg = 0


    if previous_values:

        previous_avg = (
            sum(previous_values)
            / len(previous_values)
        )

    else:

        previous_avg = 0


    # =====================================================
    # 성장률
    # =====================================================

    if previous_avg > 0:

        growth = (
            (
                recent_avg
                - previous_avg
            )
            / previous_avg
            * 100
        )

    elif recent_avg > 0:

        growth = None

    else:

        growth = 0


    # =====================================================
    # Peak
    # =====================================================

    if recent_values:

        recent_peak = max(
            recent_values
        )

    else:

        recent_peak = 0


    # =====================================================
    # 최근 검색 상승일 비중
    #
    # 최근 기간 값이 이전 기간 평균보다
    # 높은 날이 얼마나 되는지
    # =====================================================

    if (
        recent_values
        and previous_avg > 0
    ):

        above_previous = [

            value
            for value in recent_values

            if value > previous_avg
        ]


        above_previous_ratio = (
            len(above_previous)
            / len(recent_values)
            * 100
        )

    else:

        above_previous_ratio = 0


    return {

        "available":
            True,

        "search_group":
            search_group,

        "recent_30_avg":
            round(
                recent_avg,
                1
            ),

        "previous_30_avg":
            round(
                previous_avg,
                1
            ),

        "growth":
            None
            if growth is None
            else round(
                growth,
                1
            ),

        "recent_peak":
            recent_peak,

        "above_previous_ratio":
            round(
                above_previous_ratio,
                1
            )
    }


# =========================================================
# 전체 실행
# =========================================================

results = []


for brand_index, item in enumerate(
    top10,
    start=1
):

    brand = item[
        "brand"
    ]


    print()
    print("=" * 100)

    print(
        f"[{brand_index}/{len(top10)}] "
        f"{brand} 글로벌 Google Trends"
    )

    print("=" * 100)


    brand_result = {

        "brand":
            brand,

        "beauty_alpha_score":
            item.get(
                "beauty_alpha_score",
                0
            ),

        "regions":
            {}
    }


    # =====================================================
    # 국가별 분석
    # =====================================================

    for geo, region_info in REGIONS.items():

        print()

        print(
            f"🌏 {region_info['name']} "
            f"({geo})"
        )


        try:

            region_result = (
                analyze_region(
                    brand=brand,
                    geo=geo,
                    languages=region_info[
                        "languages"
                    ]
                )
            )


            brand_result[
                "regions"
            ][
                geo
            ] = region_result


            if not region_result.get(
                "available"
            ):

                print(
                    "→ 데이터 없음"
                )

            else:

                print(
                    "최근 30일 평균: "
                    f"{region_result['recent_30_avg']}"
                )

                print(
                    "이전 30일 평균: "
                    f"{region_result['previous_30_avg']}"
                )


                if region_result[
                    "growth"
                ] is None:

                    print(
                        "검색 증가율: NEW"
                    )

                else:

                    print(
                        "검색 증가율: "
                        f"{region_result['growth']}%"
                    )


                print(
                    "최근 Peak: "
                    f"{region_result['recent_peak']}"
                )


            # ---------------------------------------------
            # 요청 과다 방지
            # ---------------------------------------------

            time.sleep(
                3
            )


        except Exception as e:

            print(
                f"오류: {e}"
            )


            brand_result[
                "regions"
            ][
                geo
            ] = {

                "available":
                    False,

                "error":
                    str(e)
            }


            time.sleep(
                5
            )


    results.append(
        brand_result
    )


# =========================================================
# 글로벌 검색 신호 계산
# =========================================================

for item in results:

    positive_regions = 0

    strong_regions = 0

    available_regions = 0

    growth_values = []


    for geo, region in item[
        "regions"
    ].items():

        if not region.get(
            "available"
        ):

            continue


        available_regions += 1

        growth = region.get(
            "growth"
        )


        if growth is None:

            # 이전 관심 거의 0 →
            # 최근 검색 발생
            positive_regions += 1

            strong_regions += 1


        elif growth > 0:

            positive_regions += 1

            growth_values.append(
                growth
            )


            if growth >= 50:

                strong_regions += 1


    # =====================================================
    # 평균 성장률
    #
    # 국가별 Trends 0~100 자체를 평균내는 게 아니라
    # 각 국가 안에서 계산한 "증가율"만 참고
    # =====================================================

    if growth_values:

        avg_growth = (
            sum(growth_values)
            / len(growth_values)
        )

    else:

        avg_growth = 0


    # =====================================================
    # Global Search Score
    #
    # 절대 검색량 점수가 아니라
    # 여러 국가에서 동시 상승하는지를 측정
    # =====================================================

    global_search_score = (
        positive_regions * 10
        + strong_regions * 5
    )


    if avg_growth > 0:

        global_search_score += min(
            avg_growth / 10,
            15
        )


    item[
        "positive_regions"
    ] = positive_regions

    item[
        "strong_regions"
    ] = strong_regions

    item[
        "available_regions"
    ] = available_regions

    item[
        "average_growth"
    ] = round(
        avg_growth,
        1
    )

    item[
        "global_search_score"
    ] = round(
        global_search_score,
        1
    )


    # =====================================================
    # 라벨
    # =====================================================

    if (
        positive_regions >= 4
        and strong_regions >= 2
    ):

        item[
            "global_signal"
        ] = "🔥 글로벌 확산"


    elif positive_regions >= 3:

        item[
            "global_signal"
        ] = "📈 해외 검색 상승"


    elif positive_regions >= 1:

        item[
            "global_signal"
        ] = "👀 일부 지역 상승"


    else:

        item[
            "global_signal"
        ] = "⚪ 뚜렷한 상승 없음"


# =========================================================
# Global Search Score 순 정렬
# =========================================================

results = sorted(
    results,
    key=lambda x: x[
        "global_search_score"
    ],
    reverse=True
)


# =========================================================
# 터미널 출력
# =========================================================

print()
print()
print("=" * 110)
print("BeautyAlpha Global Search Ranking")
print("=" * 110)


for rank, item in enumerate(
    results,
    start=1
):

    print()

    print(
        f"{rank}. "
        f"{item['brand']}"
    )

    print(
        f"Global Search Score: "
        f"{item['global_search_score']}"
    )

    print(
        f"상승 국가: "
        f"{item['positive_regions']}"
        f"/"
        f"{item['available_regions']}"
    )

    print(
        f"강한 상승 국가: "
        f"{item['strong_regions']}"
    )

    print(
        f"평균 검색 증가율: "
        f"{item['average_growth']}%"
    )

    print(
        f"Global Signal: "
        f"{item['global_signal']}"
    )


    print("-" * 110)


# =========================================================
# JSON 저장
# =========================================================

with open(
    "google_trends_global.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        results,
        f,
        ensure_ascii=False,
        indent=2
    )


print()
print("=" * 110)
print(
    "저장 완료: "
    "google_trends_global.json"
)