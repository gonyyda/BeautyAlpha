import json
import os
import subprocess
import sys

import altair as alt
import pandas as pd
import streamlit as st

import ui
from run_pipeline import PIPELINE


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="BeautyAlpha",
    page_icon="💄",
    layout="wide"
)

ui.inject_css()


# =========================================================
# SAFE JSON LOADER
# =========================================================

def load_json(
    filename,
    default=None
):

    if default is None:
        default = []

    if not os.path.exists(filename):
        return default

    try:

        with open(
            filename,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except Exception as e:

        st.warning(
            f"{filename}을 불러오는 중 오류가 발생했습니다: {e}"
        )

        return default


# =========================================================
# DATA LOAD
# =========================================================

beauty_data = load_json(
    "beauty_alpha_top10.json"
)

previous_beauty_data = load_json(
    "beauty_alpha_previous.json"
)

google_data = load_json(
    "google_trends_global.json"
)

company_data = load_json(
    "company_exposure_score.json"
)

manufacturer_data = load_json(
    "manufacturer_signal.json"
)

ai_comment_data = load_json(
    "ai_research_commentary.json"
)


# =========================================================
# DICTIONARIES
# =========================================================

google_dict = {

    item.get("brand"): item

    for item in google_data

    if item.get("brand")
}


ai_comment_dict = {

    item.get("brand"): item

    for item in ai_comment_data

    if item.get("brand")
}


# =========================================================
# PREVIOUS RANK / SCORE
# =========================================================

previous_rank_dict = {}
previous_score_dict = {}


for rank, item in enumerate(
    previous_beauty_data,
    start=1
):

    brand = item.get(
        "brand"
    )

    if not brand:
        continue

    previous_rank_dict[
        brand
    ] = rank

    previous_score_dict[
        brand
    ] = item.get(
        "beauty_alpha_score",
        0
    )


# =========================================================
# RANK CHANGE
# =========================================================

def get_rank_change(
    brand,
    current_rank
):

    previous_rank = previous_rank_dict.get(
        brand
    )

    if previous_rank is None:
        return "🆕 NEW"

    change = (
        previous_rank
        - current_rank
    )

    if change > 0:
        return f"▲ {change}"

    if change < 0:
        return f"▼ {abs(change)}"

    return "－"


# =========================================================
# SCORE CHANGE
# =========================================================

def get_score_change(
    brand,
    current_score
):

    previous_score = previous_score_dict.get(
        brand
    )

    if previous_score is None:
        return None

    return round(
        current_score
        - previous_score,
        1
    )


# =========================================================
# LIST NORMALIZER
# =========================================================

def safe_list(
    value
):

    if isinstance(
        value,
        list
    ):
        return value

    return []


# =========================================================
# HERO PRODUCTS NORMALIZER
# =========================================================

def normalize_hero_products(
    value
):

    result = []

    if not isinstance(
        value,
        list
    ):
        return result

    for product in value:

        if isinstance(
            product,
            dict
        ):

            result.append(
                {
                    "product":
                        str(
                            product.get(
                                "product",
                                ""
                            )
                        ),

                    "product_strength":
                        str(
                            product.get(
                                "product_strength",
                                ""
                            )
                        ),

                    "why_it_matters":
                        str(
                            product.get(
                                "why_it_matters",
                                ""
                            )
                        )
                }
            )

        elif isinstance(
            product,
            str
        ):

            result.append(
                {
                    "product": product,
                    "product_strength": "",
                    "why_it_matters": ""
                }
            )

    return result


# =========================================================
# DRIVER NORMALIZER
# =========================================================

def normalize_drivers(
    value
):

    result = []

    if not isinstance(
        value,
        list
    ):
        return result

    for driver in value:

        if isinstance(
            driver,
            dict
        ):

            result.append(
                {
                    "label":
                        str(
                            driver.get(
                                "label",
                                ""
                            )
                        ),

                    "detail":
                        str(
                            driver.get(
                                "detail",
                                ""
                            )
                        )
                }
            )

        elif isinstance(
            driver,
            str
        ):

            result.append(
                {
                    "label": driver,
                    "detail": ""
                }
            )

    return result


# =========================================================
# REGION
# =========================================================

REGION_NAMES = {

    "KR": "🇰🇷 한국",
    "US": "🇺🇸 미국",
    "JP": "🇯🇵 일본",
    "TW": "🇹🇼 대만",
    "HK": "🇭🇰 홍콩"
}


# =========================================================
# SPREAD TEXT
# =========================================================

def get_spread_text(
    item
):

    beauty = safe_list(
        item.get(
            "beauty_creators",
            []
        )
    )

    mainstream = safe_list(
        item.get(
            "mainstream_creators",
            []
        )
    )

    global_creators = safe_list(
        item.get(
            "global_creators",
            []
        )
    )


    stages = []


    if beauty:
        stages.append(
            "🇰🇷 뷰티 전문"
        )


    if mainstream:
        stages.append(
            "🇰🇷 대중"
        )


    if global_creators:
        stages.append(
            "🌍 해외 뷰티"
        )


    if not stages:

        return item.get(
            "spread_status",
            "관측 부족"
        )


    return "  →  ".join(
        stages
    )


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        '<div class="ba-side-mark">Beauty<span>Alpha</span></div>',
        unsafe_allow_html=True
    )

    st.caption(
        "Early Beauty Trend & Investment Signal"
    )

    st.divider()

    st.markdown(
        "**데이터**"
    )


    update_button = st.button(
        "전체 데이터 업데이트",
        use_container_width=True
    )


    if update_button:

        st.warning(
            "BeautyAlpha 데이터를 업데이트하고 있습니다."
        )

        progress = st.progress(
            0
        )

        status = st.empty()

        log_box = st.empty()


        process = subprocess.Popen(
            [
                sys.executable,
                "run_pipeline.py"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1
        )


        logs = []
        step_count = 0


        for line in process.stdout:

            line = line.rstrip()

            if not line:
                continue

            logs.append(
                line
            )


            log_box.code(
                "\n".join(
                    logs[-15:]
                )
            )


            for step in range(
                1,
                len(PIPELINE) + 1
            ):

                if (
                    f"STEP {step} 완료"
                    in line
                ):

                    step_count = step


            progress.progress(
                step_count / len(PIPELINE)
            )


            status.write(
                f"업데이트 진행 중 · {step_count}/{len(PIPELINE)}"
            )


        process.wait()


        if process.returncode == 0:

            progress.progress(
                1.0
            )

            status.empty()

            st.success(
                "✅ 업데이트 완료"
            )


            if st.button(
                "✨ 최신 결과 불러오기",
                use_container_width=True
            ):

                st.rerun()


        else:

            st.error(
                "❌ 업데이트 중 오류가 발생했습니다."
            )


    st.divider()

    st.caption(
        "BeautyAlpha Score는 투자수익률 예측값이 아니라 "
        "소비·콘텐츠 확산 신호를 탐색하기 위한 실험적 지표입니다."
    )


# =========================================================
# HEADER
# =========================================================

hero_stats = []

if beauty_data:

    hero_stats.append(
        {
            "label": "현재 1위",
            "value": beauty_data[0].get("brand", "-"),
            "sub": f"Alpha {beauty_data[0].get('beauty_alpha_score', 0)}"
        }
    )

    new_entries = [
        item.get("brand")
        for item in beauty_data
        if item.get("brand") not in previous_rank_dict
    ]

    hero_stats.append(
        {
            "label": "신규 진입",
            "value": f"{len(new_entries)}개 브랜드",
            "sub": " · ".join(new_entries[:2])
        }
    )

    movers = [
        (
            get_score_change(
                item.get("brand"),
                item.get("beauty_alpha_score", 0)
            ),
            item.get("brand")
        )
        for item in beauty_data
        if item.get("brand") in previous_score_dict
    ]

    if movers:

        top_change, top_mover = max(movers)

        if top_change > 0:

            hero_stats.append(
                {
                    "label": "최대 상승",
                    "value": top_mover,
                    "sub": f"+{top_change}"
                }
            )

ui.hero(
    hero_stats
)


# =========================================================
# MAIN TABS
# =========================================================

tab1, tab2, tab3 = st.tabs(
    [
        "Market Pulse",
        "Global Signal",
        "Investment Exposure"
    ]
)


# =========================================================
# TAB 1
# =========================================================

with tab1:

    # =====================================================
    # TOP 3
    # =====================================================

    ui.section(
        "지금 주목할 브랜드",
        "최근 크리에이터 확산 속도와 BeautyAlpha Score가 높은 브랜드"
    )


    ranking_rows = []

    for rank, item in enumerate(
        beauty_data,
        start=1
    ):

        brand = item.get(
            "brand",
            "-"
        )

        score = item.get(
            "beauty_alpha_score",
            0
        )

        ranking_rows.append(
            {
                "rank": rank,
                "brand": brand,
                "score": score,
                "score_change": get_score_change(
                    brand,
                    score
                ),
                "rank_change": get_rank_change(
                    brand,
                    rank
                ),
                "signal_label": item.get(
                    "signal_label",
                    ""
                ),
                "stages": [
                    stage.strip()
                    for stage in get_spread_text(
                        item
                    ).split("→")
                ]
            }
        )


    if ranking_rows:

        ui.top3_cards(
            ranking_rows[:3]
        )


    # =====================================================
    # TOP10 RANKING
    # =====================================================

    ui.section(
        "Beauty Alpha Ranking",
        "점수가 높을수록 최근 크리에이터 확산과 Momentum이 강하게 관측됐다는 의미입니다."
    )


    if ranking_rows:

        ui.leaderboard(
            ranking_rows
        )


    # =====================================================
    # BRAND DETAIL
    # =====================================================

    ui.section(
        "브랜드 상세 분석",
        "브랜드를 선택하면 확산 지표, 제품 경쟁력, 해외 관심도를 볼 수 있습니다."
    )


    brand_names = [
        item.get("brand", "")
        for item in beauty_data
    ]

    selected_brand = st.pills(
        "브랜드 선택",
        brand_names,
        default=brand_names[0] if brand_names else None,
        label_visibility="collapsed"
    )


    for rank, item in enumerate(
        beauty_data,
        start=1
    ):

        brand = item.get(
            "brand",
            ""
        )

        if brand != selected_brand:
            continue

        score = item.get(
            "beauty_alpha_score",
            0
        )

        score_change = get_score_change(
            brand,
            score
        )

        rank_change = get_rank_change(
            brand,
            rank
        )


        if score_change is None:
            score_text = ""

        elif score_change > 0:
            score_text = (
                f" · +{score_change}"
            )

        elif score_change < 0:
            score_text = (
                f" · {score_change}"
            )

        else:
            score_text = (
                " · ±0"
            )


        with st.container(
            border=True
        ):

            st.markdown(
                f"#### {rank}. {brand}  ·  Alpha {score}{score_text}"
            )

            commentary = ai_comment_dict.get(
                brand,
                {}
            )

            google = google_dict.get(
                brand,
                {}
            )


            overview_tab, product_tab, global_tab, research_tab = st.tabs(
                [
                    "Overview",
                    "제품 경쟁력",
                    "해외 관심도",
                    "Investment View"
                ]
            )


            # =================================================
            # OVERVIEW
            # =================================================

            with overview_tab:

                st.markdown(
                    "### 핵심 지표"
                )


                c1, c2, c3, c4 = st.columns(
                    4
                )


                with c1:

                    st.metric(
                        "Beauty Alpha",
                        score,
                        delta=score_change
                    )


                with c2:

                    st.metric(
                        "Momentum",
                        item.get(
                            "momentum_score",
                            0
                        )
                    )


                with c3:

                    st.metric(
                        "최근 크리에이터",
                        item.get(
                            "recent_creator_count",
                            0
                        )
                    )


                with c4:

                    st.metric(
                        "신규 크리에이터",
                        item.get(
                            "new_creator_count",
                            0
                        )
                    )


                # =============================================
                # SPREAD
                # =============================================

                st.markdown(
                    "### 📡 확산 구조"
                )

                st.info(
                    get_spread_text(
                        item
                    )
                )


                # =============================================
                # MOMENTUM CHART
                # =============================================

                st.markdown(
                    "### 📈 언급 Momentum"
                )


                momentum_df = pd.DataFrame(
                    [
                        {
                            "기간":
                                "이전 30일",

                            "언급 영상":
                                item.get(
                                    "previous_mentions",
                                    0
                                )
                        },
                        {
                            "기간":
                                "최근 30일",

                            "언급 영상":
                                item.get(
                                    "recent_mentions",
                                    0
                                )
                        }
                    ]
                )


                momentum_chart = (
                    alt.Chart(
                        momentum_df
                    )
                    .mark_bar()
                    .encode(
                        x=alt.X(
                            "기간:N",
                            title=None,
                            sort=[
                                "이전 30일",
                                "최근 30일"
                            ],
                            axis=alt.Axis(
                                labelAngle=0,
                                labelPadding=8
                            )
                        ),
                        y=alt.Y(
                            "언급 영상:Q",
                            title="언급 영상 수"
                        ),
                        tooltip=[
                            "기간",
                            "언급 영상"
                        ]
                    )
                )


                st.altair_chart(
                    momentum_chart,
                    use_container_width=True
                )


                # =============================================
                # CREATOR COMPOSITION
                # =============================================

                st.markdown(
                    "### 👥 크리에이터 구성"
                )


                beauty_creators = safe_list(
                    item.get(
                        "beauty_creators",
                        []
                    )
                )

                mainstream_creators = safe_list(
                    item.get(
                        "mainstream_creators",
                        []
                    )
                )

                global_creators = safe_list(
                    item.get(
                        "global_creators",
                        []
                    )
                )


                creator_df = pd.DataFrame(
                    [
                        {
                            "유형":
                                "국내 뷰티",

                            "크리에이터 수":
                                len(
                                    beauty_creators
                                )
                        },
                        {
                            "유형":
                                "국내 대중",

                            "크리에이터 수":
                                len(
                                    mainstream_creators
                                )
                        },
                        {
                            "유형":
                                "해외 뷰티",

                            "크리에이터 수":
                                len(
                                    global_creators
                                )
                        }
                    ]
                )


                creator_chart = (
                    alt.Chart(
                        creator_df
                    )
                    .mark_bar()
                    .encode(
                        x=alt.X(
                            "유형:N",
                            title=None,
                            sort=[
                                "국내 뷰티",
                                "국내 대중",
                                "해외 뷰티"
                            ],
                            axis=alt.Axis(
                                labelAngle=0,
                                labelPadding=8
                            )
                        ),
                        y=alt.Y(
                            "크리에이터 수:Q",
                            title="크리에이터 수"
                        ),
                        tooltip=[
                            "유형",
                            "크리에이터 수"
                        ]
                    )
                )


                st.altair_chart(
                    creator_chart,
                    use_container_width=True
                )


                # =============================================
                # CREATOR NAMES
                # =============================================

                c1, c2, c3 = st.columns(
                    3
                )


                with c1:

                    st.markdown(
                        "**🇰🇷 뷰티 전문**"
                    )

                    st.caption(
                        ", ".join(
                            beauty_creators
                        )
                        if beauty_creators
                        else "관측 없음"
                    )


                with c2:

                    st.markdown(
                        "**🇰🇷 대중 인플루언서**"
                    )

                    st.caption(
                        ", ".join(
                            mainstream_creators
                        )
                        if mainstream_creators
                        else "관측 없음"
                    )


                with c3:

                    st.markdown(
                        "**🌍 해외 뷰티**"
                    )

                    st.caption(
                        ", ".join(
                            global_creators
                        )
                        if global_creators
                        else "관측 없음"
                    )


                # =============================================
                # WHY NOW
                # =============================================

                st.markdown(
                    "### 🚀 왜 지금 주목하나?"
                )


                drivers = normalize_drivers(
                    commentary.get(
                        "key_attention_drivers",
                        []
                    )
                )


                if drivers:

                    driver_cols = st.columns(
                        min(
                            3,
                            len(
                                drivers
                            )
                        )
                    )


                    for i, driver in enumerate(
                        drivers[:3]
                    ):

                        with driver_cols[i]:

                            label = driver.get(
                                "label",
                                ""
                            )

                            detail = driver.get(
                                "detail",
                                ""
                            )


                            st.markdown(
                                f"**{label}**"
                            )


                            if detail:

                                st.caption(
                                    detail
                                )


                else:

                    reasons = item.get(
                        "bonus_reasons",
                        []
                    )


                    if reasons:

                        for reason in reasons:

                            st.write(
                                f"• {reason}"
                            )

                    else:

                        st.caption(
                            "추가 분석 정보 없음"
                        )


            # =================================================
            # PRODUCT TAB
            # =================================================

            with product_tab:

                st.markdown(
                    "### 🧴 핵심 제품 경쟁력"
                )


                hero_products = normalize_hero_products(
                    commentary.get(
                        "hero_products",
                        []
                    )
                )


                if hero_products:

                    for product in hero_products:

                        product_name = product.get(
                            "product",
                            ""
                        )


                        if product_name:

                            st.markdown(
                                f"#### {product_name}"
                            )


                        strength = product.get(
                            "product_strength",
                            ""
                        )


                        if strength:

                            st.write(
                                strength
                            )


                        why = product.get(
                            "why_it_matters",
                            ""
                        )


                        if why:

                            st.info(
                                "💡 왜 중요한가?  "
                                + why
                            )


                        st.divider()


                else:

                    st.info(
                        "AI 제품력 분석 데이터가 없습니다."
                    )


                # =============================================
                # REVIEW
                # =============================================

                reviews = commentary.get(
                    "consumer_review_signals",
                    []
                )


                if isinstance(
                    reviews,
                    list
                ) and reviews:

                    st.markdown(
                        "### 💬 반복적으로 관측된 소비자 반응"
                    )


                    for review in reviews:

                        if isinstance(
                            review,
                            str
                        ):

                            st.write(
                                f"• {review}"
                            )


                # =============================================
                # RECENT PRODUCTS
                # =============================================

                st.markdown(
                    "### 🛍️ 최근 크리에이터 언급 제품"
                )


                recent_products = safe_list(
                    item.get(
                        "recent_products",
                        []
                    )
                )


                if recent_products:

                    for product in recent_products:

                        st.write(
                            f"• {product}"
                        )


                else:

                    st.caption(
                        "최근 제품 정보 없음"
                    )


            # =================================================
            # GLOBAL TAB
            # =================================================

            with global_tab:

                st.markdown(
                    "### 🌍 글로벌 검색 관심 변화"
                )


                if google:

                    c1, c2, c3 = st.columns(
                        3
                    )


                    with c1:

                        st.metric(
                            "Global Search Score",
                            google.get(
                                "global_search_score",
                                0
                            )
                        )


                    with c2:

                        st.metric(
                            "검색 상승 시장",
                            google.get(
                                "positive_regions",
                                0
                            )
                        )


                    with c3:

                        st.metric(
                            "강한 상승 시장",
                            google.get(
                                "strong_regions",
                                0
                            )
                        )


                    regions = google.get(
                        "regions",
                        {}
                    )


                    region_rows = []


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


                        region_rows.append(
                            {
                                "시장":
                                    REGION_NAMES.get(
                                        geo,
                                        geo
                                    ),

                                "이전 30일":
                                    region.get(
                                        "previous_30_avg",
                                        0
                                    ),

                                "최근 30일":
                                    region.get(
                                        "recent_30_avg",
                                        0
                                    )
                            }
                        )


                    if region_rows:

                        region_df = pd.DataFrame(
                            region_rows
                        )


                        region_long = region_df.melt(
                            id_vars=[
                                "시장"
                            ],
                            value_vars=[
                                "이전 30일",
                                "최근 30일"
                            ],
                            var_name="기간",
                            value_name="검색 관심도"
                        )


                        global_chart = (
                            alt.Chart(
                                region_long
                            )
                            .mark_bar()
                            .encode(
                                x=alt.X(
                                    "시장:N",
                                    title=None,
                                    axis=alt.Axis(
                                        labelAngle=0,
                                        labelPadding=8
                                    )
                                ),
                                xOffset=alt.XOffset(
                                    "기간:N"
                                ),
                                y=alt.Y(
                                    "검색 관심도:Q",
                                    title="검색 관심도"
                                ),
                                color=alt.Color(
                                    "기간:N",
                                    title=None
                                ),
                                tooltip=[
                                    "시장",
                                    "기간",
                                    "검색 관심도"
                                ]
                            )
                        )


                        st.altair_chart(
                            global_chart,
                            use_container_width=True
                        )


                    st.caption(
                        "Google Trends 값은 국가별 검색량의 절대값이 아니라 "
                        "각 시장 안에서 정규화된 관심도입니다."
                    )


                    st.markdown(
                        "### 국가별 변화"
                    )


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
                            growth_text = f"+{growth}%"

                        else:
                            growth_text = f"{growth}%"


                        st.write(
                            f"{REGION_NAMES.get(geo, geo)}  "
                            f"**{growth_text}**"
                        )


                    global_summary = commentary.get(
                        "global_signal_summary",
                        ""
                    )


                    if global_summary:

                        st.info(
                            global_summary
                        )


                else:

                    st.info(
                        "Google Trends 데이터가 없습니다."
                    )


            # =================================================
            # INVESTMENT TAB
            # =================================================

            with research_tab:

                st.markdown(
                    "### 📑 AI Research View"
                )


                research_comment = commentary.get(
                    "ai_research_comment",
                    ""
                )


                if research_comment:

                    st.write(
                        research_comment
                    )

                else:

                    st.info(
                        "AI Research Commentary가 없습니다."
                    )


                st.divider()


                # =============================================
                # CONFIDENCE
                # =============================================

                c1, c2 = st.columns(
                    2
                )


                with c1:

                    st.metric(
                        "제품 경쟁력",
                        commentary.get(
                            "product_power_level",
                            "-"
                        )
                    )


                with c2:

                    st.metric(
                        "분석 신뢰도",
                        commentary.get(
                            "confidence",
                            "-"
                        )
                    )


                # =============================================
                # WATCHPOINTS
                # =============================================

                st.markdown(
                    "### 👀 투자 관찰 포인트"
                )


                watchpoints = commentary.get(
                    "investment_watchpoints",
                    []
                )


                if isinstance(
                    watchpoints,
                    list
                ) and watchpoints:

                    for point in watchpoints:

                        st.write(
                            f"• {point}"
                        )

                else:

                    st.caption(
                        "추가 관찰 포인트 없음"
                    )


                # =============================================
                # SCORE BREAKDOWN
                # =============================================

                st.markdown(
                    "### 🧮 BeautyAlpha Score 구성"
                )


                breakdown_df = pd.DataFrame(
                    [
                        {
                            "항목":
                                "Signal Score",

                            "점수":
                                item.get(
                                    "signal_score",
                                    0
                                )
                        },
                        {
                            "항목":
                                "Momentum Score",

                            "점수":
                                item.get(
                                    "momentum_score",
                                    0
                                )
                        }
                    ]
                )


                breakdown_chart = (
                    alt.Chart(
                        breakdown_df
                    )
                    .mark_bar()
                    .encode(
                        x=alt.X(
                            "항목:N",
                            title=None,
                            axis=alt.Axis(
                                labelAngle=0,
                                labelPadding=8
                            )
                        ),
                        y=alt.Y(
                            "점수:Q",
                            title="점수"
                        ),
                        tooltip=[
                            "항목",
                            "점수"
                        ]
                    )
                )


                st.altair_chart(
                    breakdown_chart,
                    use_container_width=True
                )


                bonus_reasons = item.get(
                    "bonus_reasons",
                    []
                )


                penalty_reasons = item.get(
                    "penalty_reasons",
                    []
                )


                if bonus_reasons:

                    st.markdown(
                        "**가점 요인**"
                    )

                    for reason in bonus_reasons:

                        st.write(
                            f"＋ {reason}"
                        )


                if penalty_reasons:

                    st.markdown(
                        "**감점 요인**"
                    )

                    for reason in penalty_reasons:

                        st.write(
                            f"－ {reason}"
                        )


# =========================================================
# TAB 2 GLOBAL
# =========================================================

with tab2:

    ui.section(
        "Global Beauty Search Signal",
        "BeautyAlpha TOP 브랜드의 국가별 검색 관심 변화를 비교합니다."
    )


    google_sorted = sorted(
        google_data,
        key=lambda x: x.get(
            "global_search_score",
            0
        ),
        reverse=True
    )


    if google_sorted:

        global_ranking_rows = []


        for item in google_sorted:

            global_ranking_rows.append(
                {
                    "브랜드":
                        item.get(
                            "brand",
                            ""
                        ),

                    "Global Search":
                        item.get(
                            "global_search_score",
                            0
                        )
                }
            )


        global_ranking_df = pd.DataFrame(
            global_ranking_rows
        )


        global_ranking_chart = (
            alt.Chart(
                global_ranking_df
            )
            .mark_bar()
            .encode(
                y=alt.Y(
                    "브랜드:N",
                    sort="-x",
                    title=None
                ),
                x=alt.X(
                    "Global Search:Q",
                    title="Global Search Score"
                ),
                tooltip=[
                    "브랜드",
                    "Global Search"
                ]
            )
        )


        st.altair_chart(
            global_ranking_chart,
            use_container_width=True
        )


    st.divider()


    for rank, item in enumerate(
        google_sorted,
        start=1
    ):

        brand = item.get(
            "brand",
            ""
        )


        with st.expander(
            f"{rank}. {brand} · "
            f"Global Search {item.get('global_search_score', 0)}"
        ):

            regions = item.get(
                "regions",
                {}
            )


            rows = []


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


                rows.append(
                    {
                        "시장":
                            REGION_NAMES.get(
                                geo,
                                geo
                            ),

                        "이전 30일":
                            region.get(
                                "previous_30_avg",
                                0
                            ),

                        "최근 30일":
                            region.get(
                                "recent_30_avg",
                                0
                            )
                    }
                )


            if rows:

                chart_df = pd.DataFrame(
                    rows
                )


                chart_long = chart_df.melt(
                    id_vars=[
                        "시장"
                    ],
                    value_vars=[
                        "이전 30일",
                        "최근 30일"
                    ],
                    var_name="기간",
                    value_name="검색 관심도"
                )


                chart = (
                    alt.Chart(
                        chart_long
                    )
                    .mark_bar()
                    .encode(
                        x=alt.X(
                            "시장:N",
                            title=None,
                            axis=alt.Axis(
                                labelAngle=0,
                                labelPadding=8
                            )
                        ),
                        xOffset=alt.XOffset(
                            "기간:N"
                        ),
                        y=alt.Y(
                            "검색 관심도:Q",
                            title="검색 관심도"
                        ),
                        color=alt.Color(
                            "기간:N",
                            title=None
                        ),
                        tooltip=[
                            "시장",
                            "기간",
                            "검색 관심도"
                        ]
                    )
                )


                st.altair_chart(
                    chart,
                    use_container_width=True
                )


# =========================================================
# TAB 3 INVESTMENT EXPOSURE
# =========================================================

with tab3:

    ui.section(
        "Investment Exposure",
        "BeautyAlpha가 포착한 브랜드 신호를 "
        "브랜드 운영사와 제조사 관점으로 연결합니다."
    )


    # =====================================================
    # COMPANY
    # =====================================================

    st.markdown(
        "#### 브랜드 운영사"
    )


    if company_data:

        company_rows = []


        for item in company_data:

            company_rows.append(
                {
                    "기업":
                        item.get(
                            "company",
                            ""
                        ),

                    "Exposure":
                        item.get(
                            "company_exposure_score",
                            0
                        )
                }
            )


        company_df = pd.DataFrame(
            company_rows
        )


        company_chart = (
            alt.Chart(
                company_df
            )
            .mark_bar()
            .encode(
                y=alt.Y(
                    "기업:N",
                    sort="-x",
                    title=None
                ),
                x=alt.X(
                    "Exposure:Q",
                    title="Exposure Score"
                ),
                tooltip=[
                    "기업",
                    "Exposure"
                ]
            )
        )


        st.altair_chart(
            company_chart,
            use_container_width=True
        )


        for rank, item in enumerate(
            company_data,
            start=1
        ):

            company = item.get(
                "company",
                ""
            )


            with st.expander(
                f"{rank}. {company} · "
                f"Exposure {item.get('company_exposure_score', 0)}"
            ):

                tickers = item.get(
                    "tickers",
                    []
                )


                st.write(
                    "**종목코드:** "
                    + (
                        ", ".join(
                            tickers
                        )
                        if tickers
                        else "비상장 / 미확인"
                    )
                )


                brands = item.get(
                    "brands",
                    []
                )


                for brand in brands:

                    st.markdown(
                        f"**{brand.get('brand', '')}**"
                    )

                    st.write(
                        f"Beauty Alpha "
                        f"{brand.get('alpha_score', 0)}"
                    )

                    st.caption(
                        f"{brand.get('relation_type', '-')}"
                    )


    else:

        st.info(
            "운영사 데이터가 없습니다."
        )


    st.divider()


    # =====================================================
    # ODM
    # =====================================================

    st.markdown(
        "#### ODM / 제조사"
    )


    if manufacturer_data:

        manufacturer_rows = []


        for item in manufacturer_data:

            manufacturer_rows.append(
                {
                    "제조사":
                        item.get(
                            "manufacturer",
                            ""
                        ),

                    "Signal":
                        item.get(
                            "manufacturer_signal_score",
                            0
                        )
                }
            )


        manufacturer_df = pd.DataFrame(
            manufacturer_rows
        )


        manufacturer_chart = (
            alt.Chart(
                manufacturer_df
            )
            .mark_bar()
            .encode(
                y=alt.Y(
                    "제조사:N",
                    sort="-x",
                    title=None
                ),
                x=alt.X(
                    "Signal:Q",
                    title="Manufacturer Signal"
                ),
                tooltip=[
                    "제조사",
                    "Signal"
                ]
            )
        )


        st.altair_chart(
            manufacturer_chart,
            use_container_width=True
        )


        for rank, item in enumerate(
            manufacturer_data,
            start=1
        ):

            manufacturer = item.get(
                "manufacturer",
                ""
            )


            with st.expander(
                f"{rank}. {manufacturer} · "
                f"Signal {item.get('manufacturer_signal_score', 0)}"
            ):

                ticker = item.get(
                    "ticker",
                    ""
                )


                st.write(
                    "**종목코드:** "
                    + (
                        ticker
                        if ticker
                        else "비상장 / 미확인"
                    )
                )


                products = item.get(
                    "products",
                    []
                )


                for product in products:

                    st.markdown(
                        f"**{product.get('brand', '')} · "
                        f"{product.get('product', '')}**"
                    )

                    st.caption(
                        "✅ 제조사 확인"
                        if product.get(
                            "verified"
                        )
                        else "⚠️ 미검증"
                    )


    else:

        st.info(
            "제조사 데이터가 없습니다."
        )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "BeautyAlpha는 크리에이터 언급·검색 관심도·제품 경쟁력·기업 노출도를 "
    "조합해 초기 소비 트렌드를 탐색하는 실험적 리서치 도구입니다. "
    "점수와 AI 분석은 실제 매출 증가 또는 주가 상승을 보장하거나 "
    "직접 예측하는 지표가 아닙니다."
)