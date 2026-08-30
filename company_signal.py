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
# 브랜드 → 기업 매핑
# =========================================================

with open(
    "brand_company_map.json",
    "r",
    encoding="utf-8"
) as f:

    company_map = json.load(f)


# =========================================================
# 기업별 통계
# =========================================================

company_stats = defaultdict(
    lambda: {
        "brands": [],
        "brand_count": 0,
        "total_alpha_score": 0,
        "max_alpha_score": 0,
        "tickers": set(),
        "markets": set()
    }
)


# =========================================================
# 브랜드 데이터와 기업 매핑 합치기
# =========================================================

brand_results = []


for item in beauty_data:

    brand = item["brand"]

    mapping = company_map.get(
        brand,
        {
            "operator": "미확인",
            "parent_company": "미확인",
            "listed_company": "미확인",
            "ticker": "",
            "market": "",
            "relation_type": "",
            "verified": False
        }
    )


    combined = {
        **item,

        "operator":
            mapping.get(
                "operator",
                "미확인"
            ),

        "parent_company":
            mapping.get(
                "parent_company",
                "미확인"
            ),

        "listed_company":
            mapping.get(
                "listed_company",
                "미확인"
            ),

        "ticker":
            mapping.get(
                "ticker",
                ""
            ),

        "market":
            mapping.get(
                "market",
                ""
            ),

        "relation_type":
            mapping.get(
                "relation_type",
                ""
            ),

        "company_verified":
            mapping.get(
                "verified",
                False
            )
    }


    brand_results.append(
        combined
    )


    # =====================================================
    # 상장사별 집계
    # =====================================================

    listed_company = combined[
        "listed_company"
    ]


    if (
        listed_company
        and listed_company != "미확인"
    ):

        stats = company_stats[
            listed_company
        ]


        stats[
            "brands"
        ].append(
            {
                "brand":
                    brand,

                "beauty_alpha_score":
                    combined.get(
                        "beauty_alpha_score",
                        0
                    ),

                "verified":
                    combined.get(
                        "company_verified",
                        False
                    )
            }
        )


        stats[
            "brand_count"
        ] += 1


        alpha_score = combined.get(
            "beauty_alpha_score",
            0
        )


        stats[
            "total_alpha_score"
        ] += alpha_score


        stats[
            "max_alpha_score"
        ] = max(
            stats[
                "max_alpha_score"
            ],
            alpha_score
        )


        ticker = combined.get(
            "ticker",
            ""
        )

        if ticker:

            stats[
                "tickers"
            ].add(
                ticker
            )


        market = combined.get(
            "market",
            ""
        )

        if market:

            stats[
                "markets"
            ].add(
                market
            )


# =========================================================
# 기업 점수 계산
# =========================================================

company_results = []


for company, stats in company_stats.items():

    # -----------------------------------------------------
    # 여러 브랜드에서 동시에 신호가 나오면 보너스
    # -----------------------------------------------------

    diversification_bonus = (
        max(
            stats[
                "brand_count"
            ] - 1,
            0
        )
        * 5
    )


    # -----------------------------------------------------
    # Company Exposure Score
    #
    # 가장 강한 브랜드 신호를 중심으로 보되,
    # 여러 브랜드가 동시에 뜨면 추가 점수
    # -----------------------------------------------------

    company_exposure_score = (
        stats[
            "max_alpha_score"
        ]
        + diversification_bonus
    )


    company_results.append(
        {
            "company":
                company,

            "company_exposure_score":
                round(
                    company_exposure_score,
                    1
                ),

            "brand_count":
                stats[
                    "brand_count"
                ],

            "brands":
                sorted(
                    stats[
                        "brands"
                    ],
                    key=lambda x: x[
                        "beauty_alpha_score"
                    ],
                    reverse=True
                ),

            "tickers":
                sorted(
                    stats[
                        "tickers"
                    ]
                ),

            "markets":
                sorted(
                    stats[
                        "markets"
                    ]
                )
        }
    )


# =========================================================
# 정렬
# =========================================================

company_results = sorted(
    company_results,
    key=lambda x: x[
        "company_exposure_score"
    ],
    reverse=True
)


# =========================================================
# 출력
# =========================================================

print()
print("=" * 110)
print("BeautyAlpha Company Exposure Ranking")
print("=" * 110)


for rank, item in enumerate(
    company_results,
    start=1
):

    print()

    print(
        f"{rank}. "
        f"{item['company']}"
    )

    print(
        f"Company Exposure Score: "
        f"{item['company_exposure_score']}"
    )

    print(
        f"포착 브랜드 수: "
        f"{item['brand_count']}"
    )


    if item[
        "tickers"
    ]:

        print(
            "종목코드: "
            + ", ".join(
                item[
                    "tickers"
                ]
            )
        )


    print(
        "연결 브랜드:"
    )


    for brand in item[
        "brands"
    ]:

        verified_text = (
            "검증"
            if brand[
                "verified"
            ]
            else "미검증"
        )


        print(
            f"  - "
            f"{brand['brand']} "
            f"(Alpha "
            f"{brand['beauty_alpha_score']}, "
            f"{verified_text})"
        )


    print(
        "-" * 110
    )


# =========================================================
# 저장
# =========================================================

with open(
    "brand_investment_map.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        brand_results,
        f,
        ensure_ascii=False,
        indent=2
    )


with open(
    "company_signal.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        company_results,
        f,
        ensure_ascii=False,
        indent=2
    )


print()
print("=" * 110)

print(
    "저장 완료:"
)

print(
    "brand_investment_map.json"
)

print(
    "company_signal.json"
)