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
# 브랜드 → 기업 노출도 매핑
# =========================================================

with open(
    "company_exposure_map.json",
    "r",
    encoding="utf-8"
) as f:
    exposure_map = json.load(f)


# =========================================================
# 기업별 통계
# =========================================================

company_stats = defaultdict(
    lambda: {
        "score": 0,
        "brands": [],
        "tickers": set(),
        "markets": set()
    }
)


# =========================================================
# 브랜드별 계산
# =========================================================

for item in beauty_data:

    brand = item["brand"]

    alpha_score = item.get(
        "beauty_alpha_score",
        0
    )

    relations = exposure_map.get(
        brand,
        []
    )


    for relation in relations:

        company = relation.get(
            "company",
            ""
        )

        if not company:
            continue

        if company == "ODM 미확인":
            continue


        weight = relation.get(
            "exposure_weight",
            0
        )

        verified = relation.get(
            "verified",
            False
        )


        # ---------------------------------------------
        # 미검증 관계는 추가 할인
        # ---------------------------------------------

        verification_weight = (
            1.0
            if verified
            else 0.5
        )


        weighted_score = (
            alpha_score
            * weight
            * verification_weight
        )


        stats = company_stats[
            company
        ]

        stats[
            "score"
        ] += weighted_score


        stats[
            "brands"
        ].append(
            {
                "brand":
                    brand,

                "alpha_score":
                    alpha_score,

                "relation_type":
                    relation.get(
                        "relation_type",
                        ""
                    ),

                "exposure_weight":
                    weight,

                "verified":
                    verified,

                "contribution_score":
                    round(
                        weighted_score,
                        1
                    )
            }
        )


        ticker = relation.get(
            "ticker",
            ""
        )

        if ticker:
            stats[
                "tickers"
            ].add(
                ticker
            )


        market = relation.get(
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
# 결과 생성
# =========================================================

results = []


for company, stats in company_stats.items():

    results.append(
        {
            "company":
                company,

            "company_exposure_score":
                round(
                    stats[
                        "score"
                    ],
                    1
                ),

            "brands":
                sorted(
                    stats[
                        "brands"
                    ],
                    key=lambda x: x[
                        "contribution_score"
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


results = sorted(
    results,
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
print("BeautyAlpha Company Exposure Score")
print("=" * 110)


for rank, item in enumerate(
    results,
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
        "브랜드 기여:"
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
            f"{brand['brand']}"
            f" | Alpha "
            f"{brand['alpha_score']}"
            f" | 관계 "
            f"{brand['relation_type']}"
            f" | 가중치 "
            f"{brand['exposure_weight']}"
            f" | 기여점수 "
            f"{brand['contribution_score']}"
            f" | {verified_text}"
        )


    print(
        "-" * 110
    )


# =========================================================
# 저장
# =========================================================

with open(
    "company_exposure_score.json",
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
    "company_exposure_score.json"
)