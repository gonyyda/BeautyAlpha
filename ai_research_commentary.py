import os
import json
import time
import hashlib

from dotenv import load_dotenv
from openai import OpenAI


# =========================================================
# 기본 설정
# =========================================================

load_dotenv()

OPENAI_API_KEY = os.getenv(
    "OPENAI_API_KEY"
)

if not OPENAI_API_KEY:
    print(
        "OPENAI_API_KEY를 찾을 수 없습니다."
    )
    exit()


client = OpenAI(
    api_key=OPENAI_API_KEY
)


# =========================================================
# 파일
# =========================================================

OUTPUT_FILE = (
    "ai_research_commentary.json"
)

COMMENTARY_VERSION = (
    "beautyalpha-commentary-v3"
)


# =========================================================
# JSON 읽기
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
            f"{filename} 읽기 오류: {e}"
        )

        return default


# =========================================================
# JSON 저장
# =========================================================

def save_json(
    data
):

    with open(
        OUTPUT_FILE,
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
# 데이터 불러오기
# =========================================================

beauty_data = load_json(
    "beauty_alpha_top10.json"
)

brand_signal_data = load_json(
    "brand_signal.json"
)

momentum_data = load_json(
    "momentum_signal.json"
)

google_data = load_json(
    "google_trends_global.json"
)


# =========================================================
# 브랜드별 dictionary
# =========================================================

brand_signal_dict = {
    item.get("brand"): item
    for item in brand_signal_data
}

momentum_dict = {
    item.get("brand"): item
    for item in momentum_data
}

google_dict = {
    item.get("brand"): item
    for item in google_data
}


# =========================================================
# 기존 AI 코멘트
# =========================================================

existing_results = load_json(
    OUTPUT_FILE
)


existing_dict = {
    item.get("brand"): item
    for item in existing_results
    if item.get("brand")
}


# =========================================================
# JSON 응답 정리
# =========================================================

def clean_json_text(
    text
):

    text = text.strip()

    if text.startswith(
        "```json"
    ):

        text = text[
            len("```json"):
        ]

    elif text.startswith(
        "```"
    ):

        text = text[
            len("```"):
        ]


    if text.endswith(
        "```"
    ):

        text = text[:-3]


    return text.strip()


# =========================================================
# 현재 브랜드 데이터 묶기
#
# 이 데이터 중 하나라도 바뀌면
# AI 코멘트를 다시 생성
# =========================================================

def build_input_data(
    brand_item
):

    brand = brand_item.get(
        "brand",
        ""
    )

    signal = brand_signal_dict.get(
        brand,
        {}
    )

    momentum = momentum_dict.get(
        brand,
        {}
    )

    google = google_dict.get(
        brand,
        {}
    )


    input_data = {

        "brand":
            brand,

        "beauty_alpha_score":
            brand_item.get(
                "beauty_alpha_score",
                0
            ),

        "signal_score":
            brand_item.get(
                "signal_score",
                0
            ),

        "momentum_score":
            brand_item.get(
                "momentum_score",
                0
            ),


        # ---------------------------------------------
        # YouTube
        # ---------------------------------------------

        "recent_mentions":
            momentum.get(
                "recent_mentions",
                0
            ),

        "previous_mentions":
            momentum.get(
                "previous_mentions",
                0
            ),

        "growth_rate":
            momentum.get(
                "growth_rate"
            ),

        "recent_creator_count":
            momentum.get(
                "recent_creator_count",
                0
            ),

        "previous_creator_count":
            momentum.get(
                "previous_creator_count",
                0
            ),

        "new_creator_count":
            momentum.get(
                "new_creator_count",
                0
            ),

        "new_creators":
            momentum.get(
                "new_creators",
                []
            ),

        "beauty_creators":
            momentum.get(
                "recent_beauty_creators",
                []
            ),

        "mainstream_creators":
            momentum.get(
                "recent_mainstream_creators",
                []
            ),

        "direct_purchase_creator_count":
            momentum.get(
                "recent_direct_purchase_creator_count",
                0
            ),

        "paid_ad_creator_count":
            momentum.get(
                "recent_paid_ad_creator_count",
                0
            ),

        "recent_products":
            momentum.get(
                "recent_products",
                []
            ),


        # ---------------------------------------------
        # 기존 Signal
        # ---------------------------------------------

        "voluntary_ratio":
            signal.get(
                "voluntary_ratio",
                0
            ),

        "paid_ad_ratio":
            signal.get(
                "paid_ad_ratio",
                0
            ),


        # ---------------------------------------------
        # Google
        # ---------------------------------------------

        "global_search_score":
            google.get(
                "global_search_score",
                0
            ),

        "global_signal":
            google.get(
                "global_signal",
                ""
            ),

        "positive_regions":
            google.get(
                "positive_regions",
                0
            ),

        "regions":
            google.get(
                "regions",
                {}
            )
    }


    return input_data


# =========================================================
# 데이터 fingerprint
#
# 결과가 같으면 같은 문자열이 나오고
# 데이터가 하나라도 바뀌면 달라짐
# =========================================================

def make_signature(
    input_data
):

    signature_source = {

        "commentary_version":
            COMMENTARY_VERSION,

        "input":
            input_data
    }


    json_string = json.dumps(
        signature_source,
        ensure_ascii=False,
        sort_keys=True
    )


    return hashlib.sha256(
        json_string.encode(
            "utf-8"
        )
    ).hexdigest()


# =========================================================
# 국가별 검색 요약
# =========================================================

def make_region_summary(
    regions
):

    region_names = {
        "KR": "한국",
        "US": "미국",
        "JP": "일본",
        "TW": "대만",
        "HK": "홍콩"
    }


    summaries = []


    for geo in [
        "KR",
        "US",
        "JP",
        "TW",
        "HK"
    ]:

        region = regions.get(
            geo,
            {}
        )


        if not region.get(
            "available"
        ):
            continue


        growth = region.get(
            "growth"
        )


        if growth is None:

            growth_text = "NEW"

        elif growth > 0:

            growth_text = (
                f"+{growth}%"
            )

        else:

            growth_text = (
                f"{growth}%"
            )


        summaries.append(
            f"{region_names[geo]} "
            f"{growth_text}"
        )


    return summaries


# =========================================================
# AI 리서치
# =========================================================

def create_research_commentary(
    input_data
):

    brand = input_data[
        "brand"
    ]


    region_summary = (
        make_region_summary(
            input_data.get(
                "regions",
                {}
            )
        )
    )


    # 최대 5개 제품만 웹 리서치
    research_products = (
        input_data.get(
            "recent_products",
            []
        )[:5]
    )


    growth_rate = input_data.get(
        "growth_rate"
    )


    if growth_rate is None:

        growth_text = "NEW"

    else:

        growth_text = (
            f"{growth_rate}%"
        )


    prompt = f"""
당신은 K-Beauty 산업과 소비 트렌드를 분석하는
투자 리서치 애널리스트입니다.

BeautyAlpha가 관측한 실제 데이터를 바탕으로
웹 검색을 추가 수행해 아래 브랜드를 분석하세요.

중요:
BeautyAlpha 관측 수치는 변경하거나 추측하지 마세요.


==================================================
브랜드
==================================================

{brand}


==================================================
BeautyAlpha Signal
==================================================

Beauty Alpha Score:
{input_data["beauty_alpha_score"]}

Momentum Score:
{input_data["momentum_score"]}

최근 30일 브랜드 등장 영상:
{input_data["recent_mentions"]}

이전 30일 브랜드 등장 영상:
{input_data["previous_mentions"]}

언급 변화율:
{growth_text}

최근 크리에이터:
{input_data["recent_creator_count"]}명

이전 크리에이터:
{input_data["previous_creator_count"]}명

신규 크리에이터:
{input_data["new_creator_count"]}명

신규 크리에이터 명단:
{", ".join(input_data["new_creators"]) if input_data["new_creators"] else "없음"}

뷰티 전문 크리에이터:
{", ".join(input_data["beauty_creators"]) if input_data["beauty_creators"] else "없음"}

대중 인플루언서:
{", ".join(input_data["mainstream_creators"]) if input_data["mainstream_creators"] else "없음"}

직접구매 크리에이터:
{input_data["direct_purchase_creator_count"]}명

유료광고 크리에이터:
{input_data["paid_ad_creator_count"]}명

자발적 언급 비율:
{input_data["voluntary_ratio"]}%

유료광고 비율:
{input_data["paid_ad_ratio"]}%


==================================================
최근 언급 제품
==================================================

{json.dumps(
    research_products,
    ensure_ascii=False
)}


==================================================
Google Search Signal
==================================================

Global Search Score:
{input_data["global_search_score"]}

검색 상승 국가:
{input_data["positive_regions"]}개

Global Signal:
{input_data["global_signal"]}

국가별 검색 변화:
{", ".join(region_summary) if region_summary else "데이터 없음"}


==================================================
분석 목표
==================================================

단순한 제품 소개가 아니라

최근 확산 신호
→ 제품 경쟁력
→ 소비자 니즈
→ 콘텐츠/입소문 확산 가능성
→ 투자 관찰 포인트

순으로 분석하세요.


==================================================
제품력 웹 리서치
==================================================

최근 실제로 언급된 제품을 최우선으로 조사하세요.

가능하면 다음 정보를 교차 확인하세요.

- 공식 브랜드 페이지
- 공식 유통사
- 주요 뷰티 플랫폼
- 소비자 리뷰
- 언론 및 산업 자료


스킨케어:

- 핵심 성분
- 진정
- 보습
- 장벽
- 트러블 케어
- 제형
- 흡수감
- 끈적임
- 사용 편의성


색조:

- 발색력
- 지속력
- 밀착력
- 커버력
- 묻어남
- 색상 구성
- 퍼스널컬러 활용성
- 가루날림
- 사용 편의성


리뷰에서는 여러 소비자에게 반복적으로 나타나는
장단점을 찾아야 합니다.

단일 리뷰를 일반적인 특징처럼 표현하지 마세요.


==================================================
핵심 확산 동력
==================================================

key_attention_drivers에는
가장 중요한 2~3개만 작성하세요.

예:

- 성분 소구력
- 사용감
- 지속력
- 발색력
- 제형 차별성
- 가격 경쟁력
- 대중 확산
- 해외 검색
- 비광고성 확산

단순 키워드가 아니라

"왜 이 요소가 소비자 관심 또는
콘텐츠 확산과 맞물릴 가능성이 있는가?"

까지 설명하세요.


==================================================
제품별 Product Power
==================================================

hero_products에는
최근 실제 언급된 제품 가운데
최대 3개만 선택하세요.

각 제품에 대해:

product
제품명

product_strength
핵심 제품 경쟁력

why_it_matters
어떤 소비자 니즈와 맞고
왜 입소문이나 콘텐츠 확산에
유리할 수 있는지

를 작성하세요.


==================================================
중요: 인과관계
==================================================

제품 특징 때문에 언급이 증가했다고
단정하면 안 됩니다.

예:

잘못된 표현:
"PDRN 때문에 인기가 급증했다."

좋은 표현:
"PDRN을 비롯한 성분 메시지가
최근 소비자 관심과 맞물렸을 가능성이 있다."


==================================================
AI Research Comment
==================================================

한국어 5~8문장.

다음 순서로 작성하세요.

1. 최근 Signal
2. 크리에이터 확산 구조
3. 실제 제품력
4. 제품력과 소비자 니즈 연결
5. 검색 신호
6. 투자 관찰 포인트

광고 문구처럼 작성하지 마세요.


==================================================
출력 JSON
==================================================

JSON만 출력하세요.

{{
    "brand": "{brand}",

    "signal_summary": "",

    "diffusion_summary": "",

    "key_attention_drivers": [
        {{
            "label": "",
            "detail": ""
        }}
    ],

    "hero_products": [
        {{
            "product": "",
            "product_strength": "",
            "why_it_matters": ""
        }}
    ],

    "key_ingredients_or_features": [
        {{
            "name": "",
            "role": ""
        }}
    ],

    "consumer_review_signals": [
        ""
    ],

    "global_signal_summary": "",

    "investment_watchpoints": [
        ""
    ],

    "product_power_level":
        "strong / medium / weak / insufficient_data",

    "confidence":
        "high / medium / low",

    "ai_research_comment": ""
}}
"""


    response = client.responses.create(

        model="gpt-5.6-terra",

        reasoning={
            "effort": "low"
        },

        tools=[
            {
                "type": "web_search"
            }
        ],

        input=prompt
    )


    text = clean_json_text(
        response.output_text
    )


    result = json.loads(
        text
    )


    return result


# =========================================================
# 전체 실행
# =========================================================

new_results = []

reused_count = 0
updated_count = 0
error_count = 0


print()
print("=" * 110)

print(
    "💄 BeautyAlpha AI Commentary Update"
)

print("=" * 110)


for index, brand_item in enumerate(
    beauty_data,
    start=1
):

    brand = brand_item.get(
        "brand",
        ""
    )


    print()
    print("=" * 110)

    print(
        f"[{index}/{len(beauty_data)}] "
        f"{brand}"
    )

    print("=" * 110)


    # =====================================================
    # 현재 입력 데이터
    # =====================================================

    input_data = build_input_data(
        brand_item
    )


    current_signature = (
        make_signature(
            input_data
        )
    )


    existing = existing_dict.get(
        brand
    )


    # =====================================================
    # 기존 데이터와 완전히 동일
    # =====================================================

    if (
        existing
        and existing.get(
            "input_signature"
        ) == current_signature
        and existing.get(
            "commentary_version"
        ) == COMMENTARY_VERSION
    ):

        print(
            "♻️ 데이터 변화 없음 "
            "→ 기존 AI 코멘트 재사용"
        )


        new_results.append(
            existing
        )

        reused_count += 1

        continue


    # =====================================================
    # 신규 브랜드 또는 데이터 변화
    # =====================================================

    if existing:

        print(
            "🔄 BeautyAlpha 데이터 변화 감지"
        )

        print(
            "→ AI Research Comment 업데이트"
        )

    else:

        print(
            "🆕 신규 브랜드"
        )

        print(
            "→ AI Research Comment 생성"
        )


    try:

        research = (
            create_research_commentary(
                input_data
            )
        )


        # =================================================
        # 캐시 정보
        # =================================================

        research[
            "commentary_version"
        ] = COMMENTARY_VERSION

        research[
            "input_signature"
        ] = current_signature


        # =================================================
        # 원본 수치 저장
        # =================================================

        research[
            "beauty_alpha_score"
        ] = input_data[
            "beauty_alpha_score"
        ]

        research[
            "momentum_score"
        ] = input_data[
            "momentum_score"
        ]

        research[
            "recent_mentions"
        ] = input_data[
            "recent_mentions"
        ]

        research[
            "previous_mentions"
        ] = input_data[
            "previous_mentions"
        ]

        research[
            "growth_rate"
        ] = input_data[
            "growth_rate"
        ]

        research[
            "recent_creator_count"
        ] = input_data[
            "recent_creator_count"
        ]

        research[
            "new_creator_count"
        ] = input_data[
            "new_creator_count"
        ]

        research[
            "new_creators"
        ] = input_data[
            "new_creators"
        ]

        research[
            "beauty_creators"
        ] = input_data[
            "beauty_creators"
        ]

        research[
            "mainstream_creators"
        ] = input_data[
            "mainstream_creators"
        ]

        research[
            "global_search_score"
        ] = input_data[
            "global_search_score"
        ]

        research[
            "global_signal"
        ] = input_data[
            "global_signal"
        ]


        new_results.append(
            research
        )

        updated_count += 1


        # =================================================
        # 즉시 저장
        # =================================================

        save_json(
            new_results
        )


        print()
        print(
            "✅ AI Research Comment 업데이트 완료"
        )

        print()

        print(
            research.get(
                "ai_research_comment",
                ""
            )
        )


        time.sleep(
            2
        )


    except Exception as e:

        print(
            f"❌ AI 분석 오류: {e}"
        )


        error_count += 1


        # 기존 결과가 있다면
        # 오류가 나도 기존 결과 유지
        if existing:

            print(
                "→ 기존 코멘트를 유지합니다."
            )

            new_results.append(
                existing
            )


# =========================================================
# 최종 저장
# =========================================================

save_json(
    new_results
)


# =========================================================
# 완료
# =========================================================

print()
print("=" * 110)

print(
    "✅ AI Research Commentary 업데이트 완료"
)

print("=" * 110)

print(
    f"♻️ 기존 코멘트 재사용: "
    f"{reused_count}개"
)

print(
    f"🔄 새로 분석/업데이트: "
    f"{updated_count}개"
)

print(
    f"❌ 오류: "
    f"{error_count}개"
)

print(
    f"💾 저장 파일: "
    f"{OUTPUT_FILE}"
)