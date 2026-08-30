import json
from collections import defaultdict


# =========================================================
# Beauty Alpha 데이터
# =========================================================

with open(
    "beauty_alpha_top10.json",
    "r",
    encoding="utf-8"
) as f:

    beauty_data = json.load(f)


# =========================================================
# 제품 → 제조사 매핑
# =========================================================

with open(
    "product_manufacturer_map.json",
    "r",
    encoding="utf-8"
) as f:

    manufacturer_map = json.load(f)


# =========================================================
# 제조사별 통계
# =========================================================

manufacturer_stats = defaultdict(
    lambda: {
        "score": 0,
        "brands": set(),
        "products": [],
        "ticker": "",
        "market": ""
    }
)


# =========================================================
# 브랜드별 분석
# =========================================================

for brand_item in beauty_data:

    brand = brand_item.get(
        "brand",
        ""
    )

    alpha_score = brand_item.get(
        "beauty_alpha_score",
        0
    )

    recent_products = brand_item.get(
        "recent_products",
        []
    )


    # 브랜드 자체가 제조사 매핑에 없으면 패스
    brand_manufacturers = (
        manufacturer_map.get(
            brand,
            {}
        )
    )


    if not brand_manufacturers:
        continue


    # =====================================================
    # 최근 언급 제품과 제조사 매핑
    # =====================================================

    for recent_product in recent_products:

        recent_product_lower = (
            recent_product.lower()
        )


        for mapped_product, relations in (
            brand_manufacturers.items()
        ):

            mapped_product_lower = (
                mapped_product.lower()
            )


            # -------------------------------------------------
            # 제품명이 완전히 같지 않아도
            # 서로 포함되면 매칭
            # -------------------------------------------------

            if (
                mapped_product_lower
                not in recent_product_lower
                and
                recent_product_lower
                not in mapped_product_lower
            ):
                continue


            # -------------------------------------------------
            # 제조사별 점수 반영
            # -------------------------------------------------

            for relation in relations:

                manufacturer = relation.get(
                    "manufacturer",
                    ""
                )

                if not manufacturer:
                    continue


                verified = relation.get(
                    "verified",
                    False
                )


                # 검증된 제조관계만 강하게 반영
                verification_weight = (
                    1.0
                    if verified
                    else 0.5
                )


                # ODM 제조사는 브랜드 운영사보다
                # 실적 연결성이 낮으므로 0.4 가중치
                manufacturer_weight = 0.4


                contribution_score = (
                    alpha_score
                    * manufacturer_weight
                    * verification_weight
                )


                stats = manufacturer_stats[
                    manufacturer
                ]


                stats[
                    "score"
                ] += contribution_score


                stats[
                    "brands"
                ].add(
                    brand
                )


                stats[
                    "products"
                ].append(
                    {
                        "brand":
                            brand,

                        "product":
                            recent_product,

                        "alpha_score":
                            alpha_score,

                        "relation_type":
                            relation.get(
                                "relation_type",
                                ""
                            ),

                        "verified":
                            verified,

                        "contribution_score":
                            round(
                                contribution_score,
                                1
                            )
                    }
                )


                ticker = relation.get(
                    "ticker",
                    ""
                )

                market = relation.get(
                    "market",
                    ""
                )


                if ticker:

                    stats[
                        "ticker"
                    ] = ticker


                if market:

                    stats[
                        "market"
                    ] = market


# =========================================================
# 결과 만들기
# =========================================================

results = []


for manufacturer, stats in (
    manufacturer_stats.items()
):

    results.append(
        {
            "manufacturer":
                manufacturer,

            "manufacturer_signal_score":
                round(
                    stats[
                        "score"
                    ],
                    1
                ),

            "brand_count":
                len(
                    stats[
                        "brands"
                    ]
                ),

            "brands":
                sorted(
                    stats[
                        "brands"
                    ]
                ),

            "ticker":
                stats[
                    "ticker"
                ],

            "market":
                stats[
                    "market"
                ],

            "products":
                sorted(
                    stats[
                        "products"
                    ],
                    key=lambda x: x[
                        "contribution_score"
                    ],
                    reverse=True
                )
        }
    )


# =========================================================
# 정렬
# =========================================================

results = sorted(
    results,
    key=lambda x: x[
        "manufacturer_signal_score"
    ],
    reverse=True
)


# =========================================================
# 출력
# =========================================================

print()
print("=" * 110)

print(
    "BeautyAlpha Manufacturer Signal"
)

print("=" * 110)


for rank, item in enumerate(
    results,
    start=1
):

    print()

    print(
        f"{rank}. "
        f"{item['manufacturer']}"
    )

    print(
        f"Manufacturer Signal Score: "
        f"{item['manufacturer_signal_score']}"
    )

    print(
        f"연결 브랜드 수: "
        f"{item['brand_count']}"
    )


    if item[
        "ticker"
    ]:

        print(
            f"종목코드: "
            f"{item['ticker']}"
        )


    print(
        "연결 제품:"
    )


    for product in item[
        "products"
    ]:

        verified_text = (
            "검증"
            if product[
                "verified"
            ]
            else "미검증"
        )


        print(
            f"  - "
            f"{product['brand']} "
            f"/ "
            f"{product['product']} "
            f"| 기여점수 "
            f"{product['contribution_score']} "
            f"| {verified_text}"
        )


    print("-" * 110)


# =========================================================
# 저장
# =========================================================

with open(
    "manufacturer_signal.json",
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
    "manufacturer_signal.json"
)