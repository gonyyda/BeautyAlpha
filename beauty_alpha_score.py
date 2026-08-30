import os
import json
import shutil


# =========================================================
# 파일 설정
# =========================================================

SIGNAL_FILE = "brand_signal.json"
MOMENTUM_FILE = "momentum_signal.json"

OUTPUT_FILE = "beauty_alpha_score.json"
TOP10_FILE = "beauty_alpha_top10.json"
PREVIOUS_TOP10_FILE = "beauty_alpha_previous.json"


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
            f"❌ {filename} 읽기 오류: {e}"
        )

        return default


# =========================================================
# 데이터 불러오기
# =========================================================

signal_data = load_json(
    SIGNAL_FILE
)

momentum_data = load_json(
    MOMENTUM_FILE
)


# =========================================================
# dictionary 변환
# =========================================================

signal_dict = {

    item.get(
        "brand"
    ): item

    for item in signal_data

    if item.get(
        "brand"
    )
}


momentum_dict = {

    item.get(
        "brand"
    ): item

    for item in momentum_data

    if item.get(
        "brand"
    )
}


# =========================================================
# 전체 브랜드
# =========================================================

all_brands = sorted(
    set(
        signal_dict.keys()
    )
    |
    set(
        momentum_dict.keys()
    )
)


# =========================================================
# 결과
# =========================================================

results = []


for brand in all_brands:

    signal = signal_dict.get(
        brand,
        {}
    )

    momentum = momentum_dict.get(
        brand,
        {}
    )


    # =====================================================
    # 기본 점수
    # =====================================================

    signal_score = float(
        signal.get(
            "signal_score",
            0
        )
        or 0
    )


    momentum_score = float(
        momentum.get(
            "momentum_score",
            0
        )
        or 0
    )


    # =====================================================
    # 기본 Beauty Alpha
    #
    # Signal 30%
    # Momentum 70%
    # =====================================================

    base_score = (
        signal_score * 0.30
        +
        momentum_score * 0.70
    )


    bonus = 0
    penalty = 0

    bonus_reasons = []
    penalty_reasons = []


    # =====================================================
    # 크리에이터 정보
    # =====================================================

    recent_creator_count = int(
        momentum.get(
            "recent_creator_count",
            0
        )
        or 0
    )


    previous_creator_count = int(
        momentum.get(
            "previous_creator_count",
            0
        )
        or 0
    )


    new_creator_count = int(
        momentum.get(
            "new_creator_count",
            0
        )
        or 0
    )


    beauty_creators = momentum.get(
        "recent_beauty_creators",
        []
    ) or []


    mainstream_creators = momentum.get(
        "recent_mainstream_creators",
        []
    ) or []


    global_creators = momentum.get(
        "recent_global_creators",
        []
    ) or []


    new_global_creators = momentum.get(
        "new_global_creators",
        []
    ) or []


    global_markets = momentum.get(
        "recent_global_markets",
        []
    ) or []


    new_global_markets = momentum.get(
        "new_global_markets",
        []
    ) or []


    direct_purchase_count = int(
        momentum.get(
            "recent_direct_purchase_creator_count",
            0
        )
        or 0
    )


    paid_ad_count = int(
        momentum.get(
            "recent_paid_ad_creator_count",
            0
        )
        or 0
    )


    growth_rate = momentum.get(
        "growth_rate"
    )


    # =====================================================
    # 1. 국내 뷰티 + 국내 대중 확산
    # =====================================================

    if (
        len(beauty_creators) > 0
        and len(mainstream_creators) > 0
    ):

        bonus += 4

        bonus_reasons.append(
            "국내 뷰티→대중 확산"
        )


    # =====================================================
    # 2. 해외 크리에이터 등장
    # =====================================================

    if len(global_creators) > 0:

        global_bonus = min(
            len(global_creators) * 2.5,
            5
        )

        bonus += global_bonus

        bonus_reasons.append(
            f"해외 크리에이터 {len(global_creators)}명"
        )


    # =====================================================
    # 3. 신규 해외 크리에이터
    # =====================================================

    if len(new_global_creators) > 0:

        new_global_bonus = min(
            len(new_global_creators) * 2,
            4
        )

        bonus += new_global_bonus

        bonus_reasons.append(
            f"신규 해외 크리에이터 {len(new_global_creators)}명"
        )


    # =====================================================
    # 4. 해외 시장 다변화
    # =====================================================

    if len(global_markets) >= 2:

        bonus += 3

        bonus_reasons.append(
            f"해외 {len(global_markets)}개 시장 확산"
        )


    # =====================================================
    # 5. 신규 해외 시장
    # =====================================================

    if len(new_global_markets) > 0:

        new_market_bonus = min(
            len(new_global_markets) * 1.5,
            3
        )

        bonus += new_market_bonus

        bonus_reasons.append(
            f"신규 해외 시장 {len(new_global_markets)}개"
        )


    # =====================================================
    # 6. 신규 크리에이터 확산
    # =====================================================

    if new_creator_count >= 2:

        bonus += min(
            new_creator_count * 1.5,
            4.5
        )

        bonus_reasons.append(
            f"신규 크리에이터 {new_creator_count}명"
        )


    # =====================================================
    # 7. 직접구매 신호
    # =====================================================

    if direct_purchase_count > 0:

        direct_bonus = min(
            direct_purchase_count * 1.5,
            4.5
        )

        bonus += direct_bonus

        bonus_reasons.append(
            f"직접구매 {direct_purchase_count}명"
        )


    # =====================================================
    # 패널티 1
    # 단일 크리에이터 집중
    # =====================================================

    recent_mentions = int(
        momentum.get(
            "recent_mentions",
            0
        )
        or 0
    )


    if (
        recent_mentions >= 2
        and recent_creator_count == 1
    ):

        penalty += 5

        penalty_reasons.append(
            "단일 크리에이터 집중"
        )


    # =====================================================
    # 패널티 2
    # 최근 감소
    # =====================================================

    if (
        growth_rate is not None
        and growth_rate < 0
    ):

        penalty += 4

        penalty_reasons.append(
            "최근 언급 감소"
        )


    # =====================================================
    # 패널티 3
    # 광고 비중
    # =====================================================

    if paid_ad_count > 0:

        ad_penalty = min(
            paid_ad_count * 2,
            6
        )

        penalty += ad_penalty

        penalty_reasons.append(
            f"유료광고 {paid_ad_count}명"
        )


    # =====================================================
    # 최종 점수
    # =====================================================

    beauty_alpha_score = (
        base_score
        + bonus
        - penalty
    )


    beauty_alpha_score = max(
        0,
        min(
            round(
                beauty_alpha_score,
                1
            ),
            100
        )
    )


    # =====================================================
    # 확산 단계
    # =====================================================

    spread_steps = []


    if len(beauty_creators) > 0:

        spread_steps.append(
            "국내 뷰티"
        )


    if len(mainstream_creators) > 0:

        spread_steps.append(
            "국내 대중"
        )


    if len(global_creators) > 0:

        spread_steps.append(
            "해외 뷰티"
        )


    if spread_steps:

        spread_status = (
            " → ".join(
                spread_steps
            )
        )

    else:

        spread_status = (
            momentum.get(
                "spread_status",
                "관측 부족"
            )
        )


    # =====================================================
    # Signal Label
    # =====================================================

    if beauty_alpha_score >= 75:

        signal_label = (
            "🔥 강한 초기 확산 신호"
        )


    elif beauty_alpha_score >= 60:

        signal_label = (
            "🚀 주목할 확산 신호"
        )


    elif beauty_alpha_score >= 45:

        signal_label = (
            "👀 관찰 필요"
        )


    elif beauty_alpha_score >= 30:

        signal_label = (
            "🌱 초기 관심 신호"
        )


    else:

        signal_label = (
            "약한 신호"
        )


    # =====================================================
    # 결과
    # =====================================================

    result = {

        "brand":
            brand,

        "beauty_alpha_score":
            beauty_alpha_score,

        "base_score":
            round(
                base_score,
                1
            ),

        "signal_score":
            signal_score,

        "momentum_score":
            momentum_score,

        "bonus":
            round(
                bonus,
                1
            ),

        "penalty":
            round(
                penalty,
                1
            ),

        "bonus_reasons":
            bonus_reasons,

        "penalty_reasons":
            penalty_reasons,

        "signal_label":
            signal_label,


        # =================================================
        # Momentum
        # =================================================

        "recent_mentions":
            recent_mentions,

        "previous_mentions":
            int(
                momentum.get(
                    "previous_mentions",
                    0
                )
                or 0
            ),

        "growth_rate":
            growth_rate,

        "recent_creator_count":
            recent_creator_count,

        "previous_creator_count":
            previous_creator_count,

        "new_creator_count":
            new_creator_count,

        "new_creators":
            momentum.get(
                "new_creators",
                []
            ) or [],


        # =================================================
        # 국내
        # =================================================

        "beauty_creators":
            beauty_creators,

        "mainstream_creators":
            mainstream_creators,


        # =================================================
        # 해외
        # =================================================

        "global_creator_count":
            len(
                global_creators
            ),

        "global_creators":
            global_creators,

        "new_global_creator_count":
            len(
                new_global_creators
            ),

        "new_global_creators":
            new_global_creators,

        "global_market_count":
            len(
                global_markets
            ),

        "global_markets":
            global_markets,

        "new_global_markets":
            new_global_markets,


        # =================================================
        # 구매 / 광고
        # =================================================

        "direct_purchase_creator_count":
            direct_purchase_count,

        "paid_ad_creator_count":
            paid_ad_count,


        # =================================================
        # 제품
        # =================================================

        "recent_products":
            momentum.get(
                "recent_products",
                []
            ) or [],


        # =================================================
        # 확산
        # =================================================

        "spread_status":
            spread_status
    }


    results.append(
        result
    )


# =========================================================
# 점수순 정렬
# =========================================================

results = sorted(

    results,

    key=lambda x: x.get(
        "beauty_alpha_score",
        0
    ),

    reverse=True
)


# =========================================================
# 전체 결과 저장
# =========================================================

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
# 이전 TOP10 백업
#
# 새 TOP10을 쓰기 전에
# 기존 TOP10을 previous로 복사
# =========================================================

if os.path.exists(
    TOP10_FILE
):

    shutil.copyfile(
        TOP10_FILE,
        PREVIOUS_TOP10_FILE
    )

    print(
        "📦 이전 BeautyAlpha TOP10 백업 완료"
    )


# =========================================================
# TOP10
# =========================================================

top10 = results[:10]


# =========================================================
# TOP10 저장
# =========================================================

with open(
    TOP10_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        top10,
        f,
        ensure_ascii=False,
        indent=2
    )


# =========================================================
# 출력
# =========================================================

print()
print("=" * 110)

print(
    "💄 BeautyAlpha Score"
)

print("=" * 110)


for rank, item in enumerate(
    top10,
    start=1
):

    print()
    print(
        f"{rank}. "
        f"{item['brand']}"
    )


    print(
        f"Beauty Alpha: "
        f"{item['beauty_alpha_score']}"
    )


    print(
        f"Signal: "
        f"{item['signal_score']}"
    )


    print(
        f"Momentum: "
        f"{item['momentum_score']}"
    )


    print(
        f"기본점수: "
        f"{item['base_score']}"
    )


    print(
        f"보너스: "
        f"+{item['bonus']}"
    )


    print(
        f"패널티: "
        f"-{item['penalty']}"
    )


    print(
        f"최근 크리에이터: "
        f"{item['recent_creator_count']}명"
    )


    print(
        f"신규 크리에이터: "
        f"{item['new_creator_count']}명"
    )


    print(
        f"국내 뷰티: "
        f"{', '.join(item['beauty_creators']) or '없음'}"
    )


    print(
        f"국내 대중: "
        f"{', '.join(item['mainstream_creators']) or '없음'}"
    )


    print(
        f"🌍 해외 뷰티: "
        f"{', '.join(item['global_creators']) or '없음'}"
    )


    print(
        f"🌎 해외 시장: "
        f"{', '.join(item['global_markets']) or '없음'}"
    )


    print(
        f"확산 구조: "
        f"{item['spread_status']}"
    )


    if item[
        "bonus_reasons"
    ]:

        print(
            "가점: "
            + ", ".join(
                item[
                    "bonus_reasons"
                ]
            )
        )


    if item[
        "penalty_reasons"
    ]:

        print(
            "감점: "
            + ", ".join(
                item[
                    "penalty_reasons"
                ]
            )
        )


    print(
        f"판정: "
        f"{item['signal_label']}"
    )


print()
print("=" * 110)

print(
    f"✅ 저장 완료: "
    f"{OUTPUT_FILE}"
)

print(
    f"✅ TOP10 저장: "
    f"{TOP10_FILE}"
)

print("=" * 110)