import json
from collections import defaultdict


# =========================================================
# 파일 불러오기
# =========================================================

input_file = "product_results.json"

with open(
    input_file,
    "r",
    encoding="utf-8"
) as f:

    data = json.load(f)


# =========================================================
# 브랜드별 집계
# =========================================================

brand_stats = defaultdict(
    lambda: {
        "total_mentions": 0,
        "direct_purchase": 0,
        "product_provided": 0,
        "gift": 0,
        "paid_ad": 0,
        "co_developed": 0,
        "no_exposure_obligation": 0,
        "unclear": 0,
        "videos": set(),
        "products": set()
    }
)


# =========================================================
# 데이터 순회
# =========================================================

for video in data:

    video_title = video.get(
        "title",
        ""
    )

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
        # 뷰티도구는 일단 제외
        # 투자용 화장품 브랜드 신호 중심
        # -------------------------------------------------

        if category == "뷰티도구":
            continue


        # -------------------------------------------------
        # 너무 불완전한 제품명 제외
        # -------------------------------------------------

        if product_name:

            if (
                len(product_name) <= 2
                or product_name.isdigit()
            ):
                continue


        # -------------------------------------------------
        # 기본 언급 집계
        # -------------------------------------------------

        brand_stats[
            brand
        ][
            "total_mentions"
        ] += 1


        brand_stats[
            brand
        ][
            "videos"
        ].add(
            video_title
        )


        if product_name:

            brand_stats[
                brand
            ][
                "products"
            ].add(
                product_name
            )


        # -------------------------------------------------
        # 관계별 집계
        # -------------------------------------------------

        if relation == "직접구매":

            brand_stats[
                brand
            ][
                "direct_purchase"
            ] += 1


        elif relation == "제품제공":

            brand_stats[
                brand
            ][
                "product_provided"
            ] += 1


        elif relation == "단순선물":

            brand_stats[
                brand
            ][
                "gift"
            ] += 1


        elif relation == "유료광고":

            brand_stats[
                brand
            ][
                "paid_ad"
            ] += 1


        elif relation == "공동개발":

            brand_stats[
                brand
            ][
                "co_developed"
            ] += 1


        elif relation == "노출의무없음":

            brand_stats[
                brand
            ][
                "no_exposure_obligation"
            ] += 1


        else:

            brand_stats[
                brand
            ][
                "unclear"
            ] += 1


# =========================================================
# 정렬
# =========================================================

sorted_brands = sorted(
    brand_stats.items(),
    key=lambda x: x[1][
        "total_mentions"
    ],
    reverse=True
)


# =========================================================
# 터미널 출력
# =========================================================

print()
print("=" * 100)
print("BeautyAlpha 브랜드 언급 분석")
print("=" * 100)


for rank, (
    brand,
    stats
) in enumerate(
    sorted_brands,
    start=1
):

    print()

    print(
        f"{rank}. {brand}"
    )

    print(
        f"전체 언급: "
        f"{stats['total_mentions']}"
    )

    print(
        f"직접구매: "
        f"{stats['direct_purchase']}"
    )

    print(
        f"제품제공: "
        f"{stats['product_provided']}"
    )

    print(
        f"단순선물: "
        f"{stats['gift']}"
    )

    print(
        f"유료광고: "
        f"{stats['paid_ad']}"
    )

    print(
        f"공동개발: "
        f"{stats['co_developed']}"
    )

    print(
        f"노출의무없음: "
        f"{stats['no_exposure_obligation']}"
    )

    print(
        f"불명확: "
        f"{stats['unclear']}"
    )

    print(
        f"등장 영상 수: "
        f"{len(stats['videos'])}"
    )

    print(
        "제품:"
    )

    for product in sorted(
        stats[
            "products"
        ]
    ):

        print(
            f"  - {product}"
        )

    print("-" * 100)


# =========================================================
# JSON 저장용으로 변환
# set은 JSON 저장 불가능하므로 list로 변환
# =========================================================

output_data = []


for brand, stats in sorted_brands:

    output_data.append(
        {
            "brand": brand,

            "total_mentions":
                stats[
                    "total_mentions"
                ],

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

            "video_count":
                len(
                    stats[
                        "videos"
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
# 파일 저장
# =========================================================

output_file = (
    "brand_summary.json"
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


print()
print("=" * 100)

print(
    f"완료! 결과가 "
    f"{output_file} 파일에 저장되었습니다."
)