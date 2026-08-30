import os
import json
import time
from dotenv import load_dotenv
from openai import OpenAI


# =========================================================
# 환경변수
# =========================================================

load_dotenv()

openai_api_key = os.getenv(
    "OPENAI_API_KEY"
)

if not openai_api_key:
    print("OPENAI_API_KEY를 찾을 수 없습니다.")
    exit()


client = OpenAI(
    api_key=openai_api_key
)


# =========================================================
# JSON 읽기
# =========================================================

def load_json(filename, default=None):

    if default is None:
        default = []

    if not os.path.exists(filename):
        return default

    with open(
        filename,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


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
# 결과 파일
# =========================================================

output_file = (
    "ai_research_commentary.json"
)


# =========================================================
# 기존 결과 캐시
# =========================================================

existing_results = load_json(
    output_file
)

existing_brands = {
    item.get("brand")
    for item in existing_results
}

results = existing_results.copy()


# =========================================================
# JSON 응답 정리
# =========================================================

def clean_json_text(text):

    text = text.strip()

    if text.startswith("```json"):

        text = text[
            len("```json"):
        ]

    elif text.startswith("```"):

        text = text[
            len("```"):
        ]


    if text.endswith("```"):

        text = text[:-3]


    return text.strip()


# =========================================================
# AI Research Commentary
# =========================================================

def create_research_commentary(
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


    # =====================================================
    # Beauty Alpha 데이터
    # =====================================================

    beauty_alpha_score = (
        brand_item.get(
            "beauty_alpha_score",
            0
        )
    )

    momentum_score = (
        brand_item.get(
            "momentum_score",
            0
        )
    )


    recent_mentions = (
        momentum.get(
            "recent_mentions",
            0
        )
    )

    previous_mentions = (
        momentum.get(
            "previous_mentions",
            0
        )
    )

    growth_rate = (
        momentum.get(
            "growth_rate"
        )
    )


    recent_creator_count = (
        momentum.get(
            "recent_creator_count",
            0
        )
    )

    previous_creator_count = (
        momentum.get(
            "previous_creator_count",
            0
        )
    )


    new_creator_count = (
        momentum.get(
            "new_creator_count",
            0
        )
    )

    new_creators = (
        momentum.get(
            "new_creators",
            []
        )
    )


    beauty_creators = (
        momentum.get(
            "recent_beauty_creators",
            []
        )
    )

    mainstream_creators = (
        momentum.get(
            "recent_mainstream_creators",
            []
        )
    )


    direct_purchase_count = (
        momentum.get(
            "recent_direct_purchase_creator_count",
            0
        )
    )

    paid_ad_count = (
        momentum.get(
            "recent_paid_ad_creator_count",
            0
        )
    )


    voluntary_ratio = (
        signal.get(
            "voluntary_ratio",
            0
        )
    )

    paid_ad_ratio = (
        signal.get(
            "paid_ad_ratio",
            0
        )
    )


    recent_products = (
        momentum.get(
            "recent_products",
            []
        )
    )


    # 웹 검색 대상 제품 수 제한
    research_products = (
        recent_products[:5]
    )


    # =====================================================
    # Google Trends 데이터
    # =====================================================

    global_signal = (
        google.get(
            "global_signal",
            "데이터 없음"
        )
    )

    global_search_score = (
        google.get(
            "global_search_score",
            0
        )
    )

    positive_regions = (
        google.get(
            "positive_regions",
            0
        )
    )


    regions = google.get(
        "regions",
        {}
    )


    region_names = {
        "KR": "한국",
        "US": "미국",
        "JP": "일본",
        "TW": "대만",
        "HK": "홍콩"
    }


    region_summary = []


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

        else:

            growth_text = (
                f"{growth}%"
            )


        region_summary.append(
            f"{region_names[geo]} "
            f"{growth_text}"
        )


    # =====================================================
    # 언급 증가율 표시
    # =====================================================

    if growth_rate is None:

        youtube_growth_text = (
            "NEW"
        )

    else:

        youtube_growth_text = (
            f"{growth_rate}%"
        )


    # =====================================================
    # Prompt
    # =====================================================

    prompt = f"""
당신은 K-Beauty 산업 및 소비 트렌드를 분석하는
주식 투자 리서치 애널리스트입니다.

아래 수치는 BeautyAlpha 시스템이
YouTube 크리에이터 및 검색 데이터를 통해
직접 관측한 값입니다.

이 수치를 수정하거나 새로 만들어내지 마세요.


==================================================
[브랜드]
==================================================

{brand}


==================================================
[BeautyAlpha 관측 데이터]
==================================================

Beauty Alpha Score:
{beauty_alpha_score}

Momentum Score:
{momentum_score}

최근 30일 브랜드 등장 영상:
{recent_mentions}

이전 30일 브랜드 등장 영상:
{previous_mentions}

언급 변화율:
{youtube_growth_text}

최근 크리에이터:
{recent_creator_count}명

이전 크리에이터:
{previous_creator_count}명

신규 크리에이터:
{new_creator_count}명

신규 크리에이터 명단:
{", ".join(new_creators) if new_creators else "없음"}

뷰티 전문 크리에이터:
{", ".join(beauty_creators) if beauty_creators else "없음"}

대중 인플루언서:
{", ".join(mainstream_creators) if mainstream_creators else "없음"}

직접구매 크리에이터:
{direct_purchase_count}명

유료광고 크리에이터:
{paid_ad_count}명

자발적 언급 비율:
{voluntary_ratio}%

유료광고 비율:
{paid_ad_ratio}%


==================================================
[최근 언급 제품]
==================================================

{json.dumps(
    research_products,
    ensure_ascii=False
)}


==================================================
[Google Search Signal]
==================================================

Global Search Score:
{global_search_score}

검색 관심 상승 국가:
{positive_regions}개

Global Signal:
{global_signal}

국가별 검색 변화:
{", ".join(region_summary) if region_summary else "데이터 없음"}


==================================================
[당신의 임무]
==================================================

BeautyAlpha 관측 데이터와 웹 리서치를 결합해

"왜 이 브랜드가 최근 관심을 받을 만한가?"

를 분석하세요.

단순 제품 소개가 아니라

확산 데이터
→ 실제 제품력
→ 소비자 니즈
→ 입소문/콘텐츠 확산 가능성
→ 투자 관찰 포인트

순으로 연결해야 합니다.


==================================================
[1. 최근 확산 신호 분석]
==================================================

BeautyAlpha 데이터만 이용해 아래를 판단하세요.

- 최근 언급이 증가했는가
- 여러 서로 다른 크리에이터에게 등장했는가
- 한 명에게 집중된 신호인가
- 신규 크리에이터가 증가했는가
- 뷰티 전문군에만 머무르는가
- 대중 인플루언서까지 확산됐는가
- 광고 의존도가 높은가
- 직접구매 또는 자발적 언급 신호가 있는가


==================================================
[2. 제품력 웹 리서치]
==================================================

최근 언급 제품을 웹에서 검색하세요.

중요:
최근 실제로 언급된 제품을 최우선으로 조사하세요.

같은 브랜드의 유명 과거 제품이나
같은 라인의 다른 제품은
보조 자료로만 사용하세요.

최근 언급 제품 자체의 자료가 부족하다면
부족하다고 명시하세요.


가능하면 다음 출처를 교차 확인하세요.

- 브랜드 공식 사이트
- 공식 유통사
- 주요 뷰티 플랫폼
- 소비자 리뷰
- 신뢰할 수 있는 언론 및 산업 자료


==================================================
[3. 카테고리별 제품력]
==================================================

스킨케어라면:

- 핵심 성분
- 성분 조합
- 진정
- 보습
- 피부장벽
- 트러블 케어
- 미백
- 탄력
- 제형
- 흡수감
- 끈적임
- 민감 피부 사용성
- 사용 편의성


색조라면:

- 발색력
- 색상 구성
- 퍼스널컬러 활용성
- 밀착력
- 지속력
- 커버력
- 묻어남
- 가루날림
- 제형
- 사용 편의성
- 가격 대비 성능


헤어/바디/기타 제품은
해당 카테고리의 실제 구매 의사에 영향을 주는
제품력을 중심으로 분석하세요.


==================================================
[4. 소비자 리뷰 신호]
==================================================

리뷰에서 반복적으로 나타나는 평가가 있는지 확인하세요.

예:

- 흡수가 빠르다
- 끈적임이 적다
- 자극이 적다
- 보습력이 오래간다
- 밀착력이 좋다
- 발색이 선명하다
- 지속력이 좋다
- 컬러 구성이 실용적이다

단일 리뷰 하나를 일반화하지 마세요.

충분히 확인되지 않으면
"확인 부족"이라고 작성하세요.


==================================================
[5. 핵심 확산 동력]
==================================================

key_attention_drivers는 반드시
2~3개만 작성하세요.

label 예시:

- 성분 소구력
- 진정·장벽
- 사용감
- 제형 차별성
- 발색력
- 지속력
- 색상 구성
- 퍼스널컬러
- 가격 경쟁력
- 사용 편의성
- 대중 확산
- 해외 검색
- 비광고성 확산


detail에는 단순 제품 특징이 아니라

"왜 그 특징이 소비자 관심 또는 콘텐츠 확산과
맞물릴 가능성이 있는지"

를 한 문장으로 설명하세요.


좋은 예:

label:
성분 소구력

detail:
판테놀과 세라마이드 중심의 진정·장벽 메시지는
민감 피부 소비자가 제품 효능을 직관적으로
이해하기 쉽다는 점에서 관심 확산과 맞물릴 수 있다.


나쁜 예:

판테놀 함유.


==================================================
[6. 제품별 Product Power]
==================================================

hero_products에는
최근 실제 언급 제품 중 중요도가 높은 제품을
최대 3개까지 선택하세요.

각 제품마다:

product
실제 제품명

product_strength
성분·효과·제형·발색·지속력 등
핵심 제품력

why_it_matters
이 제품력이 어떤 소비자 니즈와 연결되고
왜 입소문이나 콘텐츠 확산에 유리할 수 있는지

를 작성하세요.


==================================================
[7. 중요한 인과관계 원칙]
==================================================

제품 특징이 최근 언급 증가의
직접적인 원인이라고 단정하지 마세요.

예:

X
"PDRN 때문에 인기가 급증했다."

O
"PDRN을 포함한 진정·장벽 중심의 성분 메시지가
최근 소비자 관심과 맞물렸을 가능성이 있다."


BeautyAlpha는 상관관계와 초기 신호를 찾는 도구이지
인과관계를 증명하는 도구가 아닙니다.


==================================================
[8. 최종 AI Research Comment]
==================================================

ai_research_comment는
한국어 5~8문장으로 작성하세요.

반드시 다음 흐름을 따르세요.


① Signal

최근 30일 BeautyAlpha 데이터에서
무엇이 달라졌는지.


② Diffusion

서로 다른 크리에이터 수,
신규 크리에이터,
뷰티 전문 → 대중 확산 여부.


③ Product Power

최근 실제 언급 제품의
가장 중요한 제품력.


④ Attention Driver

제품 특징
→ 소비자 니즈
→ 관심/입소문/콘텐츠 확산 가능성

으로 연결.


⑤ Global Confirmation

검색 데이터가 존재한다면
해외 검색 신호가 크리에이터 데이터와
같은 방향인지 다른 방향인지.


⑥ Investment Watchpoint

앞으로 무엇을 확인해야
일시적인 바이럴인지
지속적인 브랜드 성장인지 판단할 수 있는지.


==================================================
[문체]
==================================================

- 투자 리서치 문체
- 광고성 표현 금지
- 과도한 긍정 평가 금지
- 확인되지 않은 사실 금지
- 간결하지만 분석적으로 작성
- 성분 이름만 나열하지 말 것
- "왜 중요한가"까지 설명할 것


==================================================
[출력 JSON]
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


    # =====================================================
    # OpenAI + Web Search
    # =====================================================

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


    # =====================================================
    # JSON 변환
    # =====================================================

    text = clean_json_text(
        response.output_text
    )

    result = json.loads(
        text
    )


    # =====================================================
    # 원본 BeautyAlpha 데이터 강제 저장
    #
    # AI가 수치를 변경해도
    # 실제 저장값은 원본 데이터를 사용
    # =====================================================

    result[
        "beauty_alpha_score"
    ] = beauty_alpha_score

    result[
        "momentum_score"
    ] = momentum_score

    result[
        "recent_mentions"
    ] = recent_mentions

    result[
        "previous_mentions"
    ] = previous_mentions

    result[
        "growth_rate"
    ] = growth_rate

    result[
        "recent_creator_count"
    ] = recent_creator_count

    result[
        "previous_creator_count"
    ] = previous_creator_count

    result[
        "new_creator_count"
    ] = new_creator_count

    result[
        "new_creators"
    ] = new_creators

    result[
        "beauty_creators"
    ] = beauty_creators

    result[
        "mainstream_creators"
    ] = mainstream_creators

    result[
        "direct_purchase_creator_count"
    ] = direct_purchase_count

    result[
        "paid_ad_creator_count"
    ] = paid_ad_count

    result[
        "voluntary_ratio"
    ] = voluntary_ratio

    result[
        "paid_ad_ratio"
    ] = paid_ad_ratio

    result[
        "global_search_score"
    ] = global_search_score

    result[
        "global_signal"
    ] = global_signal


    return result


# =========================================================
# 전체 실행
# =========================================================

for index, brand_item in enumerate(
    beauty_data,
    start=1
):

    brand = brand_item.get(
        "brand",
        ""
    )


    print()
    print("=" * 100)

    print(
        f"[{index}/{len(beauty_data)}] "
        f"{brand}"
    )

    print("=" * 100)


    # =====================================================
    # 기존 결과 있으면 건너뛰기
    # =====================================================

    if brand in existing_brands:

        print(
            "기존 AI Research Comment 있음 → 건너뜀"
        )

        continue


    print(
        "BeautyAlpha Signal + 제품력 웹 리서치 분석 중..."
    )


    try:

        research = (
            create_research_commentary(
                brand_item
            )
        )


        results.append(
            research
        )

        existing_brands.add(
            brand
        )


        # =================================================
        # 즉시 저장
        # =================================================

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                results,
                f,
                ensure_ascii=False,
                indent=2
            )


        # =================================================
        # 터미널 미리보기
        # =================================================

        print()
        print("🚀 핵심 확산 동력")
        print("-" * 100)


        for driver in research.get(
            "key_attention_drivers",
            []
        ):

            print(
                f"• "
                f"{driver.get('label', '')}: "
                f"{driver.get('detail', '')}"
            )


        print()
        print("🧴 Product Power")
        print("-" * 100)


        for product in research.get(
            "hero_products",
            []
        ):

            print(
                f"• "
                f"{product.get('product', '')}"
            )

            print(
                f"  제품력: "
                f"{product.get('product_strength', '')}"
            )

            print(
                f"  의미: "
                f"{product.get('why_it_matters', '')}"
            )


        print()
        print("✨ AI Research Insight")
        print("-" * 100)

        print(
            research.get(
                "ai_research_comment",
                ""
            )
        )


        print()
        print("👀 Watchpoints")
        print("-" * 100)


        for point in research.get(
            "investment_watchpoints",
            []
        ):

            print(
                f"• {point}"
            )


        time.sleep(
            2
        )


    except Exception as e:

        print(
            f"오류 발생: {e}"
        )

        time.sleep(
            3
        )


# =========================================================
# 최종 저장
# =========================================================

with open(
    output_file,
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
print("=" * 100)

print(
    "BeautyAlpha AI Research Commentary 완료"
)

print(
    f"저장 파일: "
    f"{output_file}"
)

print(
    f"분석 브랜드: "
    f"{len(results)}개"
)