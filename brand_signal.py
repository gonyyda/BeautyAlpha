import json
from collections import defaultdict


# =========================================================
# 입력 파일
# =========================================================

input_file = "all_product_results_60d.json"


# creators.json 의 creator_type → 내부 분류
CREATOR_TYPE_ALIASES = {
    "KR_BEAUTY": "beauty",
    "KR_MAINSTREAM": "mainstream",
    "GLOBAL_BEAUTY_EN": "global_beauty"
}

with open(
    input_file,
    "r",
    encoding="utf-8"
) as f:

    data = json.load(f)


# =========================================================
# 브랜드별 통계 구조
# =========================================================

brand_stats = defaultdict(
    lambda: {
        "total_mentions": 0,

        "beauty_mentions": 0,
        "mainstream_mentions": 0,

        "direct_purchase": 0,
        "product_provided": 0,
        "gift": 0,
        "paid_ad": 0,
        "co_developed": 0,
        "no_exposure_obligation": 0,
        "unclear": 0,

        "creators": set(),
        "beauty_creators": set(),
        "mainstream_creators": set(),

        "videos": set(),
        "products": set()
    }
)


# =========================================================
# 데이터 집계
# =========================================================

for video in data:

    creator = video.get(
        "creator",
        ""
    ).strip()

    creator_type = video.get(
        "creator_type",
        ""
    ).strip()

    creator_type = CREATOR_TYPE_ALIASES.get(
        creator_type,
        creator_type
    )

    video_title = video.get(
        "title",
        ""
    ).strip()

    products = video.get(
        "products",
        []
    )


    for product in products:

        brand = product.get(
            "brand",
            ""
        ).strip()

        product_name = product.get(
            "product",
            ""
        ).strip()

        category = product.get(
            "category",
            ""
        ).strip()

        relation = product.get(
            "commercial_relation",
            "불명확"
        ).strip()


        # -------------------------------------------------
        # 브랜드명이 없으면 제외
        # -------------------------------------------------

        if not brand:
            continue


        # -------------------------------------------------
        # 뷰티도구 제외
        # -------------------------------------------------

        if category == "뷰티도구":
            continue


        # -------------------------------------------------
        # 불완전한 제품명 제외
        # -------------------------------------------------

        if product_name:

            if (
                len(product_name) <= 2
                or product_name.isdigit()
            ):
                continue


        stats = brand_stats[
            brand
        ]


        # -------------------------------------------------
        # 전체 언급
        # -------------------------------------------------

        stats[
            "total_mentions"
        ] += 1


        if creator:

            stats[
                "creators"
            ].add(
                creator
            )


        if video_title:

            stats[
                "videos"
            ].add(
                video_title
            )


        if product_name:

            stats[
                "products"
            ].add(
                product_name
            )


        # -------------------------------------------------
        # 크리에이터 유형별 집계
        # -------------------------------------------------

        if creator_type == "beauty":

            stats[
                "beauty_mentions"
            ] += 1

            if creator:

                stats[
                    "beauty_creators"
                ].add(
                    creator
                )


        elif creator_type == "mainstream":

            stats[
                "mainstream_mentions"
            ] += 1

            if creator:

                stats[
                    "mainstream_creators"
                ].add(
                    creator
                )


        # -------------------------------------------------
        # 상업적 관계별 집계
        # -------------------------------------------------

        if relation == "직접구매":

            stats[
                "direct_purchase"
            ] += 1


        elif relation == "제품제공":

            stats[
                "product_provided"
            ] += 1


        elif relation == "단순선물":

            stats[
                "gift"
            ] += 1


        elif relation == "유료광고":

            stats[
                "paid_ad"
            ] += 1


        elif relation == "공동개발":

            stats[
                "co_developed"
            ] += 1


        elif relation == "노출의무없음":

            stats[
                "no_exposure_obligation"
            ] += 1


        else:

            stats[
                "unclear"
            ] += 1


# =========================================================
# Signal Score 계산
# =========================================================

output_data = []


for brand, stats in brand_stats.items():

    unique_creators = len(
        stats[
            "creators"
        ]
    )

    beauty_creator_count = len(
        stats[
            "beauty_creators"
        ]
    )

    mainstream_creator_count = len(
        stats[
            "mainstream_creators"
        ]
    )


    # -----------------------------------------------------
    # 자발적 언급 계산
    #
    # 직접구매를 가장 강한 자발적 신호로 봄
    #
    # 노출의무없음도 어느 정도 자발성이 있다고 보고 포함
    #
    # 불명확은 자발적이라고 단정하지 않음
    # -----------------------------------------------------

    voluntary_mentions = (
        stats["direct_purchase"]
        + stats["no_exposure_obligation"]
    )


    if stats[
        "total_mentions"
    ] > 0:

        voluntary_ratio = (
            voluntary_mentions
            / stats["total_mentions"]
            * 100
        )

    else:

        voluntary_ratio = 0


    # -----------------------------------------------------
    # 광고 비율
    # -----------------------------------------------------

    if stats[
        "total_mentions"
    ] > 0:

        paid_ad_ratio = (
            stats["paid_ad"]
            / stats["total_mentions"]
            * 100
        )

    else:

        paid_ad_ratio = 0


    # -----------------------------------------------------
    # BeautyAlpha Signal Score v2
    #
    # 핵심 철학
    #
    # 1. 여러 서로 다른 크리에이터가 언급했는가?
    # 2. 직접 구매인가?
    # 3. 대중 인플루언서에게까지 확산됐는가?
    # 4. 뷰티 전문군에서도 관찰되는가?
    # 5. 광고 의존도가 높은가?
    # -----------------------------------------------------

    signal_score = (
        unique_creators * 5
        + stats["direct_purchase"] * 4
        + mainstream_creator_count * 4
        + beauty_creator_count * 2
        + stats["total_mentions"] * 1
        - stats["paid_ad"] * 3
        - stats["product_provided"] * 1
    )


    # -----------------------------------------------------
    # 확산 상태
    # -----------------------------------------------------

    if (
        beauty_creator_count > 0
        and mainstream_creator_count > 0
    ):

        spread_status = (
            "뷰티 전문군 + 대중 확산"
        )

    elif (
        beauty_creator_count > 0
        and mainstream_creator_count == 0
    ):

        spread_status = (
            "뷰티 전문군 중심"
        )

    elif (
        beauty_creator_count == 0
        and mainstream_creator_count > 0
    ):

        spread_status = (
            "대중 인플루언서 중심"
        )

    else:

        spread_status = (
            "확산 정보 부족"
        )


    # -----------------------------------------------------
    # 결과 저장
    # -----------------------------------------------------

    output_data.append(
        {
            "brand": brand,

            "signal_score":
                signal_score,

            "spread_status":
                spread_status,

            "total_mentions":
                stats[
                    "total_mentions"
                ],

            "unique_creator_count":
                unique_creators,

            "beauty_mentions":
                stats[
                    "beauty_mentions"
                ],

            "mainstream_mentions":
                stats[
                    "mainstream_mentions"
                ],

            "beauty_creator_count":
                beauty_creator_count,

            "mainstream_creator_count":
                mainstream_creator_count,

            "direct_purchase":
                stats[
                    "direct_purchase"
                ],

            "product_provided":
                stats[
                    "product_provided"
                ],

            "gift":
                stats[
                    "gift"
                ],

            "paid_ad":
                stats[
                    "paid_ad"
                ],

            "co_developed":
                stats[
                    "co_developed"
                ],

            "no_exposure_obligation":
                stats[
                    "no_exposure_obligation"
                ],

            "unclear":
                stats[
                    "unclear"
                ],

            "voluntary_mentions":
                voluntary_mentions,

            "voluntary_ratio":
                round(
                    voluntary_ratio,
                    1
                ),

            "paid_ad_ratio":
                round(
                    paid_ad_ratio,
                    1
                ),

            "creators":
                sorted(
                    stats[
                        "creators"
                    ]
                ),

            "beauty_creators":
                sorted(
                    stats[
                        "beauty_creators"
                    ]
                ),

            "mainstream_creators":
                sorted(
                    stats[
                        "mainstream_creators"
                    ]
                ),

            "products":
                sorted(
                    stats[
                        "products"
                    ]
                )
        }
    )


# =========================================================
# Signal Score 순으로 정렬
# =========================================================

output_data = sorted(
    output_data,
    key=lambda x: x[
        "signal_score"
    ],
    reverse=True
)


# =========================================================
# 상위 10개
# =========================================================

top_10 = output_data[:10]


# =========================================================
# 터미널 출력
# =========================================================

print()
print("=" * 110)
print("BeautyAlpha Brand Signal Ranking TOP 10")
print("=" * 110)


for rank, item in enumerate(
    top_10,
    start=1
):

    print()

    print(
        f"{rank}. "
        f"{item['brand']}"
    )

    print(
        f"Signal Score: "
        f"{item['signal_score']}"
    )

    print(
        f"확산 상태: "
        f"{item['spread_status']}"
    )

    print(
        f"총 언급: "
        f"{item['total_mentions']}"
    )

    print(
        f"서로 다른 크리에이터: "
        f"{item['unique_creator_count']}명"
    )

    print(
        f"뷰티 전문군: "
        f"{item['beauty_mentions']}회 "
        f"/ "
        f"{item['beauty_creator_count']}명"
    )

    print(
        f"대중 인플루언서군: "
        f"{item['mainstream_mentions']}회 "
        f"/ "
        f"{item['mainstream_creator_count']}명"
    )

    print(
        f"직접구매: "
        f"{item['direct_purchase']}"
    )

    print(
        f"제품제공: "
        f"{item['product_provided']}"
    )

    print(
        f"유료광고: "
        f"{item['paid_ad']}"
    )

    print(
        f"자발적 언급: "
        f"{item['voluntary_mentions']}"
    )

    print(
        f"자발적 언급 비율: "
        f"{item['voluntary_ratio']}%"
    )

    print(
        f"유료광고 비율: "
        f"{item['paid_ad_ratio']}%"
    )

    print(
        "언급 크리에이터: "
        + ", ".join(
            item[
                "creators"
            ]
        )
    )

    print("-" * 110)


# =========================================================
# 전체 JSON 저장
# =========================================================

output_file = (
    "brand_signal.json"
)

with open(
    output_file,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        output_data,
        f,
        ensure_ascii=False,
        indent=2
    )


# =========================================================
# TOP 10 JSON 저장
# =========================================================

top10_file = (
    "brand_signal_top10.json"
)

with open(
    top10_file,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        top_10,
        f,
        ensure_ascii=False,
        indent=2
    )


# =========================================================
# 완료 메시지
# =========================================================

print()
print("=" * 110)

print(
    f"전체 결과 저장: "
    f"{output_file}"
)

print(
    f"TOP 10 저장: "
    f"{top10_file}"
)