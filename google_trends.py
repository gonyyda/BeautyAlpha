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
# Google Trends 연결
#
# hl="ko-KR"
# tz=-540 : 한국 시간 기준
# =========================================================

pytrends = TrendReq(
    hl="ko-KR",
    tz=-540
)


# =========================================================
# 브랜드별 결과
# =========================================================

results = []


for index, item in enumerate(
    top10,
    start=1
):

    brand = item["brand"]

    print()
    print("=" * 90)
    print(
        f"[{index}/{len(top10)}] "
        f"{brand} Google Trends 분석"
    )
    print("=" * 90)


    try:

        # -------------------------------------------------
        # 최근 3개월 / 한국 검색 관심도
        # -------------------------------------------------

        pytrends.build_payload(
            kw_list=[brand],
            cat=0,
            timeframe="today 3-m",
            geo="KR",
            gprop=""
        )


        trend_data = (
            pytrends.interest_over_time()
        )


        # 데이터가 없는 경우
        if trend_data.empty:

            print(
                "검색 데이터 없음"
            )

            results.append(
                {
                    "brand": brand,
                    "trend_available": False,
                    "recent_30_avg": 0,
                    "previous_30_avg": 0,
                    "trend_growth": None
                }
            )

            continue


        # -------------------------------------------------
        # isPartial 제외
        # -------------------------------------------------

        if "isPartial" in trend_data.columns:

            trend_data = trend_data.drop(
                columns=[
                    "isPartial"
                ]
            )


        values = (
            trend_data[
                brand
            ]
            .tolist()
        )


        # -------------------------------------------------
        # 최근 약 30일
        #
        # Google Trends 일별 데이터 기준으로
        # 마지막 30개 값을 이용
        # -------------------------------------------------

        recent_values = (
            values[-30:]
        )


        previous_values = (
            values[-60:-30]
        )


        # -------------------------------------------------
        # 평균 계산
        # -------------------------------------------------

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


        # -------------------------------------------------
        # 검색 관심도 증가율
        # -------------------------------------------------

        if previous_avg > 0:

            trend_growth = (
                (
                    recent_avg
                    - previous_avg
                )
                / previous_avg
                * 100
            )

        elif recent_avg > 0:

            trend_growth = None

        else:

            trend_growth = 0


        # -------------------------------------------------
        # 최근 최고 검색 관심도
        # -------------------------------------------------

        recent_peak = (
            max(recent_values)
            if recent_values
            else 0
        )


        # -------------------------------------------------
        # 결과
        # -------------------------------------------------

        result = {
            "brand":
                brand,

            "trend_available":
                True,

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

            "trend_growth":
                None
                if trend_growth is None
                else round(
                    trend_growth,
                    1
                ),

            "recent_peak":
                recent_peak
        }


        results.append(
            result
        )


        print(
            f"최근 30일 평균 관심도: "
            f"{result['recent_30_avg']}"
        )

        print(
            f"이전 30일 평균 관심도: "
            f"{result['previous_30_avg']}"
        )


        if result[
            "trend_growth"
        ] is None:

            print(
                "Google 검색 증가율: NEW"
            )

        else:

            print(
                f"Google 검색 증가율: "
                f"{result['trend_growth']}%"
            )


        print(
            f"최근 최고 관심도: "
            f"{recent_peak}"
        )


        # -------------------------------------------------
        # 너무 빠른 요청 방지
        # -------------------------------------------------

        time.sleep(3)


    except Exception as e:

        print(
            f"Google Trends 오류: {e}"
        )

        results.append(
            {
                "brand": brand,
                "trend_available": False,
                "error": str(e)
            }
        )

        time.sleep(5)


# =========================================================
# 저장
# =========================================================

with open(
    "google_trends_results.json",
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
print("=" * 90)
print(
    "Google Trends 분석 완료"
)
print(
    "저장 파일: "
    "google_trends_results.json"
)