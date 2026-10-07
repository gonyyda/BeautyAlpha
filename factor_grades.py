import json
import os
from datetime import datetime


# =========================================================
# 파일 설정
# =========================================================

SCORE_FILE = "beauty_alpha_score.json"
GOOGLE_FILE = "google_trends_global.json"

OUTPUT_FILE = "factor_grades.json"
HISTORY_FILE = "beauty_alpha_history.json"

# 기록에는 점수 상위 브랜드만 남긴다
HISTORY_TOP_N = 50


# =========================================================
# 팩터 설정
# =========================================================

FACTORS = [
    "buzz",
    "momentum",
    "spread",
    "authenticity",
    "search"
]

# Trend Rating 가중치 (없는 팩터는 제외하고 다시 정규화)
FACTOR_WEIGHTS = {
    "buzz": 0.25,
    "momentum": 0.30,
    "spread": 0.20,
    "authenticity": 0.15,
    "search": 0.10
}

# 백분위 하한 → 등급
GRADE_STEPS = [
    (0.95, "A+"),
    (0.85, "A"),
    (0.75, "A-"),
    (0.65, "B+"),
    (0.55, "B"),
    (0.45, "B-"),
    (0.35, "C+"),
    (0.25, "C"),
    (0.15, "C-"),
    (0.05, "D")
]

RATING_STEPS = [
    (0.80, "Strong Signal"),
    (0.60, "Signal"),
    (0.40, "Neutral"),
    (0.20, "Fading")
]


# =========================================================
# JSON
# =========================================================

def load_json(
    filename,
    default
):

    if not os.path.exists(filename):
        return default

    with open(
        filename,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


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
# 팩터 원점수
# =========================================================

def number(
    item,
    key
):

    return float(
        item.get(key) or 0
    )


def raw_buzz(item):

    # 최근 30일 언급 크리에이터 수가 중심, 언급 횟수는 보조
    return (
        number(item, "recent_creator_count")
        + 0.1 * number(item, "recent_mentions")
    )


def raw_momentum(item):

    return number(
        item,
        "momentum_score"
    )


def raw_spread(item):

    # 뷰티 전문 → 대중 → 해외 단계와 해외 시장 수
    stages = sum(
        1
        for key in (
            "beauty_creators",
            "mainstream_creators",
            "global_creators"
        )
        if item.get(key)
    )

    return (
        stages
        + 0.25 * min(
            number(item, "global_market_count"),
            4
        )
    )


RAW_FUNCTIONS = {
    "buzz": raw_buzz,
    "momentum": raw_momentum,
    "spread": raw_spread
}


def authenticity_of(item):

    # 직접구매는 올리고 유료광고는 내린다. 둘 다 없으면 중간(0.5).
    # 최근 언급이 없으면 판단할 근거가 없다.
    creators = number(
        item,
        "recent_creator_count"
    )

    if creators <= 0:
        return None

    share = (
        number(item, "direct_purchase_creator_count")
        - number(item, "paid_ad_creator_count")
    ) / creators

    return max(
        0.0,
        min(
            1.0,
            0.5 + 0.5 * share
        )
    )


# =========================================================
# 백분위 / 등급
# =========================================================

def percentile_of(
    value,
    positive_values
):

    # 신호가 있는(0보다 큰) 브랜드끼리의 상대 순위. 동점은 중간 순위.
    if value <= 0 or not positive_values:
        return 0.0

    below = sum(
        1
        for other in positive_values
        if other < value
    )

    equal = sum(
        1
        for other in positive_values
        if other == value
    )

    return (
        below + 0.5 * equal
    ) / len(positive_values)


def grade_of(percentile):

    for threshold, grade in GRADE_STEPS:

        if percentile >= threshold:
            return grade

    return "F"


def rating_of(score):

    for threshold, rating in RATING_STEPS:

        if score >= threshold:
            return rating

    return "Weak"


# =========================================================
# 계산
# =========================================================

def build_grades(
    score_data,
    google_data
):

    search_scores = {
        item.get("brand"): item.get("global_search_score")
        for item in google_data
        if item.get("brand")
        and item.get("global_search_score") is not None
    }

    raw = {
        factor: {}
        for factor in RAW_FUNCTIONS
    }

    for item in score_data:

        brand = item.get("brand")

        if not brand:
            continue

        for factor, function in RAW_FUNCTIONS.items():

            raw[factor][brand] = function(item)

    positive_raw = {
        factor: [
            value
            for value in values.values()
            if value > 0
        ]
        for factor, values in raw.items()
    }

    items_by_brand = {
        item.get("brand"): item
        for item in score_data
    }

    results = []

    for rank, item in enumerate(
        sorted(
            score_data,
            key=lambda x: x.get("beauty_alpha_score", 0),
            reverse=True
        ),
        start=1
    ):

        brand = item.get("brand")

        if not brand:
            continue

        percentiles = {}

        for factor in RAW_FUNCTIONS:

            percentiles[factor] = percentile_of(
                raw[factor][brand],
                positive_raw[factor]
            )

        authenticity = authenticity_of(
            items_by_brand[brand]
        )

        if authenticity is not None:
            percentiles["authenticity"] = authenticity

        # 검색 관심도는 일부 브랜드만 조회하므로 0~100 점수를 그대로 쓴다
        if brand in search_scores:

            percentiles["search"] = max(
                0.0,
                min(
                    1.0,
                    float(search_scores[brand]) / 100
                )
            )

        weight_sum = sum(
            FACTOR_WEIGHTS[factor]
            for factor in percentiles
        )

        rating_score = (
            sum(
                FACTOR_WEIGHTS[factor] * value
                for factor, value in percentiles.items()
            ) / weight_sum
            if weight_sum
            else 0.0
        )

        results.append(
            {
                "brand": brand,
                "rank": rank,
                "beauty_alpha_score": item.get(
                    "beauty_alpha_score",
                    0
                ),
                "trend_rating": rating_of(rating_score),
                "rating_score": round(rating_score, 3),
                "factors": {
                    factor: (
                        {
                            "grade": grade_of(percentiles[factor]),
                            "percentile": round(percentiles[factor], 3)
                        }
                        if factor in percentiles
                        else None
                    )
                    for factor in FACTORS
                }
            }
        )

    return results


# =========================================================
# 기록
# =========================================================

def update_history(
    history,
    results,
    today
):

    snapshot = {
        "date": today,
        "brands": {
            item["brand"]: {
                "score": item["beauty_alpha_score"],
                "rank": item["rank"],
                "rating": item["trend_rating"]
            }
            for item in results[:HISTORY_TOP_N]
        }
    }

    # 같은 날 다시 실행하면 그날 기록을 교체
    snapshots = [
        entry
        for entry in history.get("snapshots", [])
        if entry.get("date") != today
    ]

    snapshots.append(snapshot)

    snapshots.sort(
        key=lambda entry: entry.get("date", "")
    )

    return {
        "snapshots": snapshots
    }


# =========================================================
# 실행
# =========================================================

def main():

    score_data = load_json(
        SCORE_FILE,
        []
    )

    if not score_data:

        print(
            f"{SCORE_FILE}에 데이터가 없습니다."
        )

        raise SystemExit(1)

    google_data = load_json(
        GOOGLE_FILE,
        []
    )

    results = build_grades(
        score_data,
        google_data
    )

    save_json(
        OUTPUT_FILE,
        results
    )

    today = datetime.now().strftime(
        "%Y-%m-%d"
    )

    history = update_history(
        load_json(
            HISTORY_FILE,
            {}
        ),
        results,
        today
    )

    save_json(
        HISTORY_FILE,
        history
    )

    print("=" * 110)
    print("Factor Grades TOP 10")
    print("=" * 110)

    for item in results[:10]:

        grades = "  ".join(
            f"{factor}:{(item['factors'][factor] or {}).get('grade', '-')}"
            for factor in FACTORS
        )

        print(
            f"{item['rank']:>2}. {item['brand']} | "
            f"{item['trend_rating']} | {grades}"
        )

    print()

    print(
        f"등급 저장: {OUTPUT_FILE} ({len(results)}개 브랜드)"
    )

    print(
        f"기록 저장: {HISTORY_FILE} "
        f"({len(history['snapshots'])}회차, {today})"
    )


if __name__ == "__main__":

    main()
