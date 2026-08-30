import json
from datetime import datetime, timedelta, timezone


# =========================================================
# 파일 설정
# =========================================================

INPUT_FILE = "all_product_results_60d.json"
OUTPUT_FILE = "momentum_signal.json"


RECENT_DAYS = 30
PREVIOUS_DAYS = 30


# =========================================================
# JSON 불러오기
# =========================================================

with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as f:

    videos = json.load(f)


# =========================================================
# 날짜 기준
# =========================================================

now = datetime.now(
    timezone.utc
)

recent_cutoff = (
    now
    - timedelta(
        days=RECENT_DAYS
    )
)

previous_cutoff = (
    now
    - timedelta(
        days=RECENT_DAYS + PREVIOUS_DAYS
    )
)


# =========================================================
# 날짜 파싱
# =========================================================

def parse_date(
    value
):

    return datetime.fromisoformat(
        value.replace(
            "Z",
            "+00:00"
        )
    )


# =========================================================
# 브랜드명 정리
# =========================================================

def normalize_brand(
    brand
):

    if not brand:
        return ""

    return (
        str(brand)
        .strip()
    )


# =========================================================
# brand_data 구조
# =========================================================

brand_data = {}


def get_brand_data(
    brand
):

    if brand not in brand_data:

        brand_data[
            brand
        ] = {

            # ---------------------------------------------
            # 최근 / 이전 영상
            # ---------------------------------------------

            "recent_video_ids":
                set(),

            "previous_video_ids":
                set(),


            # ---------------------------------------------
            # 전체 크리에이터
            # ---------------------------------------------

            "recent_creators":
                set(),

            "previous_creators":
                set(),


            # ---------------------------------------------
            # 국내 뷰티 전문
            # ---------------------------------------------

            "recent_beauty_creators":
                set(),

            "previous_beauty_creators":
                set(),


            # ---------------------------------------------
            # 국내 대중
            # ---------------------------------------------

            "recent_mainstream_creators":
                set(),

            "previous_mainstream_creators":
                set(),


            # ---------------------------------------------
            # 해외 뷰티
            # ---------------------------------------------

            "recent_global_creators":
                set(),

            "previous_global_creators":
                set(),


            # ---------------------------------------------
            # 해외 시장
            # ---------------------------------------------

            "recent_global_markets":
                set(),

            "previous_global_markets":
                set(),


            # ---------------------------------------------
            # 구매 / 광고
            # ---------------------------------------------

            "recent_direct_purchase_creators":
                set(),

            "recent_paid_ad_creators":
                set(),


            # ---------------------------------------------
            # 최근 제품
            # ---------------------------------------------

            "recent_products":
                set()
        }


    return brand_data[
        brand
    ]


# =========================================================
# 영상별 처리
#
# 중요:
# 같은 영상에서 같은 브랜드 제품이 여러 개 나와도
# 브랜드 언급은 영상 1개로만 계산
# =========================================================

for video in videos:

    published_at = video.get(
        "published_at"
    )


    if not published_at:
        continue


    try:

        published_date = parse_date(
            published_at
        )

    except Exception:
        continue


    # 60일보다 오래된 데이터 제외
    if published_date < previous_cutoff:
        continue


    video_id = video.get(
        "video_id",
        ""
    )


    creator = video.get(
        "creator",
        ""
    )


    creator_type = video.get(
        "creator_type",
        ""
    )


    market = video.get(
        "market",
        "KR"
    )


    products = video.get(
        "products",
        []
    )


    # =====================================================
    # 한 영상 안에서 같은 브랜드 중복 제거
    # =====================================================

    brands_in_video = {}


    for product in products:

        if not isinstance(
            product,
            dict
        ):
            continue


        brand = normalize_brand(
            product.get(
                "brand"
            )
        )


        if not brand:
            continue


        if brand not in brands_in_video:

            brands_in_video[
                brand
            ] = {

                "products":
                    set(),

                "direct_purchase":
                    False,

                "paid_ad":
                    False
            }


        product_name = str(
            product.get(
                "product",
                ""
            )
        ).strip()


        if product_name:

            brands_in_video[
                brand
            ][
                "products"
            ].add(
                product_name
            )


        commercial_relation = str(
            product.get(
                "commercial_relation",
                ""
            )
        )


        if (
            "직접구매"
            in commercial_relation
        ):

            brands_in_video[
                brand
            ][
                "direct_purchase"
            ] = True


        if (
            "유료광고"
            in commercial_relation
        ):

            brands_in_video[
                brand
            ][
                "paid_ad"
            ] = True


    # =====================================================
    # 브랜드별 반영
    # =====================================================

    for brand, brand_video_info in (
        brands_in_video.items()
    ):

        data = get_brand_data(
            brand
        )


        # =================================================
        # 최근 30일
        # =================================================

        if published_date >= recent_cutoff:

            data[
                "recent_video_ids"
            ].add(
                video_id
            )


            data[
                "recent_creators"
            ].add(
                creator
            )


            # ---------------------------------------------
            # 국내 뷰티 전문
            # ---------------------------------------------

            if creator_type == "beauty":

                data[
                    "recent_beauty_creators"
                ].add(
                    creator
                )


            # ---------------------------------------------
            # 국내 대중 인플루언서
            # ---------------------------------------------

            elif creator_type == "mainstream":

                data[
                    "recent_mainstream_creators"
                ].add(
                    creator
                )


            # ---------------------------------------------
            # 해외 뷰티
            # ---------------------------------------------

            elif creator_type == "global_beauty":

                data[
                    "recent_global_creators"
                ].add(
                    creator
                )

                if market:

                    data[
                        "recent_global_markets"
                    ].add(
                        market
                    )


            # ---------------------------------------------
            # 직접구매
            # ---------------------------------------------

            if brand_video_info[
                "direct_purchase"
            ]:

                data[
                    "recent_direct_purchase_creators"
                ].add(
                    creator
                )


            # ---------------------------------------------
            # 광고
            # ---------------------------------------------

            if brand_video_info[
                "paid_ad"
            ]:

                data[
                    "recent_paid_ad_creators"
                ].add(
                    creator
                )


            # ---------------------------------------------
            # 최근 제품
            # ---------------------------------------------

            for product_name in (
                brand_video_info[
                    "products"
                ]
            ):

                data[
                    "recent_products"
                ].add(
                    product_name
                )


        # =================================================
        # 이전 30일
        # =================================================

        else:

            data[
                "previous_video_ids"
            ].add(
                video_id
            )


            data[
                "previous_creators"
            ].add(
                creator
            )


            if creator_type == "beauty":

                data[
                    "previous_beauty_creators"
                ].add(
                    creator
                )


            elif creator_type == "mainstream":

                data[
                    "previous_mainstream_creators"
                ].add(
                    creator
                )


            elif creator_type == "global_beauty":

                data[
                    "previous_global_creators"
                ].add(
                    creator
                )

                if market:

                    data[
                        "previous_global_markets"
                    ].add(
                        market
                    )


# =========================================================
# 최종 Momentum 계산
# =========================================================

results = []


for brand, data in (
    brand_data.items()
):

    recent_mentions = len(
        data[
            "recent_video_ids"
        ]
    )


    previous_mentions = len(
        data[
            "previous_video_ids"
        ]
    )


    recent_creators = (
        data[
            "recent_creators"
        ]
    )


    previous_creators = (
        data[
            "previous_creators"
        ]
    )


    new_creators = (
        recent_creators
        - previous_creators
    )


    recent_beauty = (
        data[
            "recent_beauty_creators"
        ]
    )


    recent_mainstream = (
        data[
            "recent_mainstream_creators"
        ]
    )


    recent_global = (
        data[
            "recent_global_creators"
        ]
    )


    previous_global = (
        data[
            "previous_global_creators"
        ]
    )


    new_global_creators = (
        recent_global
        - previous_global
    )


    recent_global_markets = (
        data[
            "recent_global_markets"
        ]
    )


    previous_global_markets = (
        data[
            "previous_global_markets"
        ]
    )


    new_global_markets = (
        recent_global_markets
        - previous_global_markets
    )


    # =====================================================
    # 증가율
    # =====================================================

    if previous_mentions == 0:

        if recent_mentions > 0:
            growth_rate = None

        else:
            growth_rate = 0

    else:

        growth_rate = round(
            (
                recent_mentions
                - previous_mentions
            )
            / previous_mentions
            * 100,
            1
        )


    # =====================================================
    # Momentum Score
    #
    # 해외 확산을 별도 보너스로 반영
    # =====================================================

    score = 0


    # -----------------------------------------------------
    # 최근 언급 영상
    # -----------------------------------------------------

    score += min(
        recent_mentions * 8,
        32
    )


    # -----------------------------------------------------
    # 최근 고유 크리에이터
    # -----------------------------------------------------

    score += min(
        len(recent_creators) * 7,
        28
    )


    # -----------------------------------------------------
    # 신규 크리에이터
    # -----------------------------------------------------

    score += min(
        len(new_creators) * 6,
        18
    )


    # -----------------------------------------------------
    # 국내 전문 → 국내 대중 확산
    # -----------------------------------------------------

    if (
        len(recent_beauty) > 0
        and len(recent_mainstream) > 0
    ):

        score += 8


    # -----------------------------------------------------
    # 해외 뷰티 크리에이터 등장
    # -----------------------------------------------------

    if len(recent_global) > 0:

        score += min(
            len(recent_global) * 6,
            12
        )


    # -----------------------------------------------------
    # 신규 해외 크리에이터
    # -----------------------------------------------------

    if len(new_global_creators) > 0:

        score += min(
            len(new_global_creators) * 5,
            10
        )


    # -----------------------------------------------------
    # 여러 해외 시장 확산
    # -----------------------------------------------------

    if len(recent_global_markets) >= 2:

        score += 5


    # -----------------------------------------------------
    # 신규 해외 시장
    # -----------------------------------------------------

    if len(new_global_markets) > 0:

        score += min(
            len(new_global_markets) * 3,
            6
        )


    # -----------------------------------------------------
    # 직접구매 보너스
    # -----------------------------------------------------

    direct_purchase_count = len(
        data[
            "recent_direct_purchase_creators"
        ]
    )


    score += min(
        direct_purchase_count * 3,
        9
    )


    # -----------------------------------------------------
    # 광고 패널티
    # -----------------------------------------------------

    paid_ad_count = len(
        data[
            "recent_paid_ad_creators"
        ]
    )


    score -= min(
        paid_ad_count * 3,
        9
    )


    # -----------------------------------------------------
    # 단일 크리에이터 집중 패널티
    # -----------------------------------------------------

    if (
        recent_mentions >= 2
        and len(recent_creators) == 1
    ):

        score -= 8


    # -----------------------------------------------------
    # 감소 패널티
    # -----------------------------------------------------

    if (
        growth_rate is not None
        and growth_rate < 0
    ):

        score -= 8


    score = max(
        0,
        min(
            round(
                score,
                1
            ),
            100
        )
    )


    # =====================================================
    # 확산 상태
    # =====================================================

    spread_parts = []


    if len(recent_beauty) > 0:

        spread_parts.append(
            "국내 뷰티"
        )


    if len(recent_mainstream) > 0:

        spread_parts.append(
            "국내 대중"
        )


    if len(recent_global) > 0:

        spread_parts.append(
            "해외 뷰티"
        )


    if spread_parts:

        spread_status = (
            " → ".join(
                spread_parts
            )
        )

    else:

        spread_status = (
            "관측 부족"
        )


    # =====================================================
    # 결과
    # =====================================================

    results.append(
        {

            "brand":
                brand,

            "momentum_score":
                score,

            "recent_mentions":
                recent_mentions,

            "previous_mentions":
                previous_mentions,

            "growth_rate":
                growth_rate,

            "recent_creator_count":
                len(
                    recent_creators
                ),

            "previous_creator_count":
                len(
                    previous_creators
                ),

            "new_creator_count":
                len(
                    new_creators
                ),

            "new_creators":
                sorted(
                    new_creators
                ),


            # ---------------------------------------------
            # 국내
            # ---------------------------------------------

            "recent_beauty_creators":
                sorted(
                    recent_beauty
                ),

            "recent_mainstream_creators":
                sorted(
                    recent_mainstream
                ),


            # ---------------------------------------------
            # 해외
            # ---------------------------------------------

            "recent_global_creator_count":
                len(
                    recent_global
                ),

            "recent_global_creators":
                sorted(
                    recent_global
                ),

            "previous_global_creator_count":
                len(
                    previous_global
                ),

            "new_global_creator_count":
                len(
                    new_global_creators
                ),

            "new_global_creators":
                sorted(
                    new_global_creators
                ),

            "recent_global_market_count":
                len(
                    recent_global_markets
                ),

            "recent_global_markets":
                sorted(
                    recent_global_markets
                ),

            "new_global_markets":
                sorted(
                    new_global_markets
                ),


            # ---------------------------------------------
            # 광고 / 구매
            # ---------------------------------------------

            "recent_direct_purchase_creator_count":
                direct_purchase_count,

            "recent_paid_ad_creator_count":
                paid_ad_count,


            # ---------------------------------------------
            # 제품
            # ---------------------------------------------

            "recent_products":
                sorted(
                    data[
                        "recent_products"
                    ]
                ),


            # ---------------------------------------------
            # 확산 상태
            # ---------------------------------------------

            "spread_status":
                spread_status
        }
    )


# =========================================================
# Momentum 순 정렬
# =========================================================

results = sorted(
    results,
    key=lambda x: x.get(
        "momentum_score",
        0
    ),
    reverse=True
)


# =========================================================
# 저장
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
# 결과 출력
# =========================================================

print()
print("=" * 100)
print("🌍 BeautyAlpha Momentum Signal")
print("=" * 100)


for rank, item in enumerate(
    results[:20],
    start=1
):

    print()
    print(
        f"{rank}. "
        f"{item['brand']}"
    )

    print(
        f"Momentum Score: "
        f"{item['momentum_score']}"
    )

    print(
        f"최근 / 이전 언급: "
        f"{item['recent_mentions']} / "
        f"{item['previous_mentions']}"
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
        f"{', '.join(item['recent_beauty_creators']) or '없음'}"
    )

    print(
        f"국내 대중: "
        f"{', '.join(item['recent_mainstream_creators']) or '없음'}"
    )

    print(
        f"🌍 해외 뷰티: "
        f"{', '.join(item['recent_global_creators']) or '없음'}"
    )

    print(
        f"🌎 해외 시장: "
        f"{', '.join(item['recent_global_markets']) or '없음'}"
    )

    print(
        f"확산 구조: "
        f"{item['spread_status']}"
    )


print()
print(
    f"✅ 저장 완료: "
    f"{OUTPUT_FILE}"
)