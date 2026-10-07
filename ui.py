import html

import streamlit as st


# =========================================================
# GLOBAL CSS
# =========================================================

CSS = """
<style>
@import url("https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css");

:root {
    --ba-rose: #D6457A;
    --ba-rose-soft: #FCE8EC;
    --ba-plum: #6B2D4E;
    --ba-ink: #2B1F24;
    --ba-muted: #8A7078;
    --ba-line: #F0D9DE;
    --ba-card: #FFFFFF;
    --ba-gold: #C89B6D;
    --ba-up: #1F8A5F;
    --ba-down: #C2493A;
}

.stApp, .stApp p, .stApp li, .stApp label, .stApp input, .stApp button,
.stApp h1, .stApp h2, .stApp h3, .stApp h4,
[data-testid="stMarkdownContainer"], [data-testid="stMetricValue"] {
    font-family: "Pretendard", -apple-system, "Malgun Gothic", sans-serif;
}

.block-container {
    padding-top: 2.2rem;
    max-width: 1240px;
}

/* ---------- hero ---------- */

.ba-hero {
    background: linear-gradient(120deg, #FCE8EC 0%, #FBEFE9 55%, #F6E6F0 100%);
    border: 1px solid var(--ba-line);
    border-radius: 28px;
    padding: 34px 38px;
    display: flex;
    flex-wrap: wrap;
    gap: 28px;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 22px;
}

.ba-hero-main { flex: 1 1 300px; min-width: 0; }

.ba-eyebrow {
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--ba-rose);
}

.ba-wordmark {
    font-size: 46px;
    font-weight: 800;
    letter-spacing: -0.03em;
    line-height: 1.1;
    color: var(--ba-ink);
    margin: 6px 0 10px;
}

.ba-wordmark span { color: var(--ba-rose); }

.ba-lede {
    font-size: 15px;
    line-height: 1.6;
    color: var(--ba-muted);
    max-width: 520px;
}

.ba-flow { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 16px; }

.ba-flow span {
    background: rgba(255, 255, 255, 0.75);
    border: 1px solid var(--ba-line);
    border-radius: 999px;
    padding: 4px 12px;
    font-size: 12px;
    font-weight: 500;
    color: var(--ba-plum);
}

.ba-hero-stats { display: flex; flex-wrap: wrap; gap: 10px; }

.ba-stat {
    background: var(--ba-card);
    border: 1px solid var(--ba-line);
    border-radius: 20px;
    padding: 14px 16px;
    min-width: 108px;
}

.ba-stat-label { font-size: 12px; color: var(--ba-muted); }

.ba-stat-value {
    font-size: 19px;
    font-weight: 700;
    color: var(--ba-ink);
    margin-top: 4px;
    white-space: nowrap;
}

.ba-stat-sub { font-size: 12px; font-weight: 600; color: var(--ba-rose); margin-top: 2px; }

/* ---------- section title ---------- */

.ba-section { margin: 30px 0 14px; }

.ba-section-title {
    font-size: 22px;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: var(--ba-ink);
}

.ba-section-caption { font-size: 14px; color: var(--ba-muted); margin-top: 2px; }

/* ---------- top 3 cards ---------- */

.ba-top3 {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
    gap: 16px;
}

.ba-card {
    background: var(--ba-card);
    border: 1px solid var(--ba-line);
    border-radius: 24px;
    padding: 24px;
    box-shadow: 0 10px 30px -22px rgba(107, 45, 78, 0.45);
    min-width: 0;
}

.ba-card.is-first {
    background: linear-gradient(160deg, #FFFFFF 0%, #FDEEF2 100%);
    border-color: #EFC4D0;
}

.ba-card-head { display: flex; align-items: center; justify-content: space-between; gap: 8px; }

.ba-rank {
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.12em;
    color: var(--ba-gold);
}

.ba-brand {
    font-size: 24px;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: var(--ba-ink);
    margin-top: 10px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.ba-score-row { display: flex; align-items: baseline; gap: 10px; margin-top: 12px; }

.ba-score {
    font-size: 44px;
    font-weight: 800;
    letter-spacing: -0.03em;
    line-height: 1;
    color: var(--ba-rose);
    font-variant-numeric: tabular-nums;
}

.ba-score-label { font-size: 12px; color: var(--ba-muted); margin-top: 6px; }

.ba-signal { font-size: 14px; font-weight: 600; color: var(--ba-plum); margin-top: 16px; }

.ba-chips { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }

.ba-chip {
    background: var(--ba-rose-soft);
    border-radius: 999px;
    padding: 3px 10px;
    font-size: 12px;
    font-weight: 500;
    color: var(--ba-plum);
    white-space: nowrap;
}

/* ---------- change pills ---------- */

.ba-pill {
    display: inline-block;
    border-radius: 999px;
    padding: 2px 9px;
    font-size: 12px;
    font-weight: 600;
    white-space: nowrap;
    font-variant-numeric: tabular-nums;
}

.ba-pill.up { background: #E4F4EC; color: var(--ba-up); }
.ba-pill.down { background: #FBE7E3; color: var(--ba-down); }
.ba-pill.flat { background: #F3ECEE; color: var(--ba-muted); }
.ba-pill.new { background: var(--ba-rose); color: #FFFFFF; }

/* ---------- leaderboard ---------- */

.ba-board {
    background: var(--ba-card);
    border: 1px solid var(--ba-line);
    border-radius: 24px;
    padding: 10px 22px;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
    column-gap: 40px;
}

.ba-row {
    display: grid;
    grid-template-columns: 26px minmax(0, 1.1fr) minmax(60px, 1.4fr) 46px 58px;
    align-items: center;
    gap: 12px;
    padding: 11px 0;
    border-bottom: 1px solid #F7E9EC;
}

.ba-row-rank { font-size: 13px; font-weight: 700; color: var(--ba-gold); text-align: center; }

.ba-row-brand {
    font-size: 15px;
    font-weight: 600;
    color: var(--ba-ink);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.ba-bar { height: 8px; border-radius: 999px; background: #F8E7EB; overflow: hidden; }

.ba-bar i {
    display: block;
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #EFA3BA, #D6457A);
}

.ba-row-score {
    font-size: 15px;
    font-weight: 700;
    color: var(--ba-ink);
    text-align: right;
    font-variant-numeric: tabular-nums;
}

.ba-row-change { text-align: right; }

/* ---------- trend rating ---------- */

.ba-rating {
    display: inline-block;
    border-radius: 8px;
    padding: 3px 10px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.02em;
    white-space: nowrap;
}

.ba-rating.strong { background: var(--ba-rose); color: #FFFFFF; }
.ba-rating.signal { background: #F8CDD8; color: #8E2A4E; }
.ba-rating.neutral { background: #F3ECEE; color: var(--ba-muted); }
.ba-rating.fading { background: #F6E9DC; color: #8A6234; }
.ba-rating.weak { background: #ECECEC; color: #6F6F6F; }

.ba-card-rating { margin-top: 8px; }

.ba-row-name { min-width: 0; }

.ba-row-rating { font-size: 11px; font-weight: 600; margin-top: 1px; }

.ba-row-rating.strong, .ba-row-rating.signal { color: var(--ba-rose); }
.ba-row-rating.neutral, .ba-row-rating.fading, .ba-row-rating.weak { color: var(--ba-muted); }

/* ---------- factor grades ---------- */

.ba-factors {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(108px, 1fr));
    gap: 10px;
    margin: 6px 0 18px;
}

.ba-factor {
    background: var(--ba-card);
    border: 1px solid var(--ba-line);
    border-radius: 16px;
    padding: 14px 16px;
}

.ba-factor-name { font-size: 13px; font-weight: 600; color: var(--ba-ink); }

.ba-factor-grade {
    font-size: 30px;
    font-weight: 800;
    letter-spacing: -0.02em;
    line-height: 1.2;
    margin-top: 4px;
}

.ba-factor-grade.a { color: var(--ba-rose); }
.ba-factor-grade.b { color: var(--ba-plum); }
.ba-factor-grade.c { color: var(--ba-gold); }
.ba-factor-grade.d { color: var(--ba-muted); }
.ba-factor-grade.none { color: #CDBFC4; }

.ba-factor-desc { font-size: 12px; color: var(--ba-muted); margin-top: 2px; }

.ba-detail-head { display: flex; flex-wrap: wrap; align-items: center; gap: 10px; margin-bottom: 4px; }

.ba-detail-title { font-size: 22px; font-weight: 700; letter-spacing: -0.02em; color: var(--ba-ink); }

.ba-detail-meta { font-size: 14px; color: var(--ba-muted); }

/* ---------- streamlit widgets ---------- */

[data-testid="stMetric"] {
    background: var(--ba-card);
    border: 1px solid var(--ba-line);
    border-radius: 18px;
    padding: 14px 18px;
}

[data-testid="stMetricLabel"] p { color: var(--ba-muted); font-size: 13px; }

[data-testid="stMetricValue"] { font-weight: 700; letter-spacing: -0.02em; }

[data-testid="stExpander"] details {
    background: var(--ba-card);
    border: 1px solid var(--ba-line);
    border-radius: 18px;
}

[data-testid="stExpander"] summary p { font-weight: 600; }

.stTabs [data-baseweb="tab-list"] { gap: 6px; border-bottom: none; }

.stTabs [data-baseweb="tab"] {
    border-radius: 999px;
    padding: 6px 18px;
    height: auto;
    background: transparent;
}

.stTabs [aria-selected="true"] { background: var(--ba-rose-soft); }

.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"],
.stTabs [role="tablist"]::after { display: none; }

.stButton > button { border-radius: 999px; font-weight: 600; }

[data-testid="stSidebar"] .ba-side-mark {
    font-size: 22px;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: var(--ba-ink);
}

[data-testid="stSidebar"] .ba-side-mark span { color: var(--ba-rose); }

@media (max-width: 640px) {
    .ba-hero { padding: 24px 20px; border-radius: 22px; }
    .ba-wordmark { font-size: 36px; }
    .ba-score { font-size: 38px; }
    .ba-row { grid-template-columns: 22px minmax(0, 1fr) 44px 56px; }
    .ba-row .ba-bar { display: none; }
}
</style>
"""


def inject_css():

    st.markdown(
        CSS,
        unsafe_allow_html=True
    )


def _render(markup):

    st.markdown(
        markup,
        unsafe_allow_html=True
    )


def _esc(value):

    return html.escape(
        str(value)
    )


# =========================================================
# CHANGE PILLS
# =========================================================

def rank_pill(rank_change):

    if "NEW" in rank_change:
        return '<span class="ba-pill new">NEW</span>'

    if rank_change.startswith("▲"):
        return f'<span class="ba-pill up">{_esc(rank_change)}</span>'

    if rank_change.startswith("▼"):
        return f'<span class="ba-pill down">{_esc(rank_change)}</span>'

    return '<span class="ba-pill flat">유지</span>'


def score_pill(score_change):

    if score_change is None:
        return ""

    if score_change > 0:
        return f'<span class="ba-pill up">+{score_change}</span>'

    if score_change < 0:
        return f'<span class="ba-pill down">{score_change}</span>'

    return '<span class="ba-pill flat">±0</span>'


# =========================================================
# HERO
# =========================================================

def hero(stats):

    stats_html = "".join(
        '<div class="ba-stat">'
        f'<div class="ba-stat-label">{_esc(s["label"])}</div>'
        f'<div class="ba-stat-value">{_esc(s["value"])}</div>'
        f'<div class="ba-stat-sub">{_esc(s.get("sub", ""))}</div>'
        '</div>'
        for s in stats
    )

    flow = [
        "크리에이터 언급",
        "대중 확산",
        "해외 확산",
        "검색 관심",
        "제품 경쟁력",
        "관련 기업"
    ]

    flow_html = "".join(
        f"<span>{_esc(step)}</span>"
        for step in flow
    )

    _render(
        '<div class="ba-hero">'
        '<div class="ba-hero-main">'
        '<div class="ba-eyebrow">Early Beauty Trend &amp; Investment Signal</div>'
        '<div class="ba-wordmark">Beauty<span>Alpha</span></div>'
        '<div class="ba-lede">크리에이터의 첫 언급부터 관련 기업까지, '
        '뷰티 트렌드가 퍼져 나가는 흐름을 한 화면에서 읽습니다.</div>'
        f'<div class="ba-flow">{flow_html}</div>'
        '</div>'
        f'<div class="ba-hero-stats">{stats_html}</div>'
        '</div>'
    )


# =========================================================
# SECTION TITLE
# =========================================================

def section(title, caption=""):

    caption_html = (
        f'<div class="ba-section-caption">{_esc(caption)}</div>'
        if caption
        else ""
    )

    _render(
        '<div class="ba-section">'
        f'<div class="ba-section-title">{_esc(title)}</div>'
        f'{caption_html}'
        '</div>'
    )


# =========================================================
# TOP 3 CARDS
# =========================================================

def top3_cards(cards):

    labels = [
        "NO. 1",
        "NO. 2",
        "NO. 3"
    ]

    parts = []

    for i, card in enumerate(cards):

        chips = "".join(
            f'<span class="ba-chip">{_esc(stage)}</span>'
            for stage in card["stages"]
        )

        first = " is-first" if i == 0 else ""

        parts.append(
            f'<div class="ba-card{first}">'
            '<div class="ba-card-head">'
            f'<span class="ba-rank">{labels[i]}</span>'
            f'{rank_pill(card["rank_change"])}'
            '</div>'
            f'<div class="ba-brand">{_esc(card["brand"])}</div>'
            f'<div class="ba-card-rating">{rating_badge(card.get("rating"))}</div>'
            '<div class="ba-score-row">'
            f'<span class="ba-score">{_esc(card["score"])}</span>'
            f'{score_pill(card["score_change"])}'
            '</div>'
            '<div class="ba-score-label">Beauty Alpha Score</div>'
            f'<div class="ba-signal">{_esc(card["signal_label"])}</div>'
            f'<div class="ba-chips">{chips}</div>'
            '</div>'
        )

    _render(
        f'<div class="ba-top3">{"".join(parts)}</div>'
    )


# =========================================================
# LEADERBOARD
# =========================================================

def leaderboard(rows):

    max_score = max(
        [row["score"] for row in rows] + [1]
    )

    parts = []

    for row in rows:

        width = max(
            2,
            round(row["score"] / max_score * 100)
        )

        parts.append(
            '<div class="ba-row">'
            f'<div class="ba-row-rank">{row["rank"]}</div>'
            '<div class="ba-row-name">'
            f'<div class="ba-row-brand">{_esc(row["brand"])}</div>'
            f'{row_rating(row.get("rating"))}'
            '</div>'
            f'<div class="ba-bar"><i style="width:{width}%"></i></div>'
            f'<div class="ba-row-score">{_esc(row["score"])}</div>'
            f'<div class="ba-row-change">{rank_pill(row["rank_change"])}</div>'
            '</div>'
        )

    half = (len(parts) + 1) // 2

    columns = "".join(
        f'<div>{"".join(chunk)}</div>'
        for chunk in (parts[:half], parts[half:])
        if chunk
    )

    _render(
        f'<div class="ba-board">{columns}</div>'
    )
# =========================================================
# TREND RATING / FACTOR GRADES
# =========================================================

RATING_CLASSES = {
    "Strong Signal": "strong",
    "Signal": "signal",
    "Neutral": "neutral",
    "Fading": "fading",
    "Weak": "weak"
}

FACTOR_LABELS = [
    ("buzz", "Buzz", "지금 언급되는 정도"),
    ("momentum", "Momentum", "늘어나는 속도"),
    ("spread", "Spread", "전문 → 대중 → 해외"),
    ("authenticity", "Authenticity", "광고 아닌 자발 언급"),
    ("search", "Search", "검색 관심으로 연결")
]


def rating_badge(rating):

    if not rating:
        return ""

    return (
        f'<span class="ba-rating {RATING_CLASSES.get(rating, "neutral")}">'
        f'{_esc(rating)}</span>'
    )


def row_rating(rating):

    if not rating:
        return ""

    return (
        f'<div class="ba-row-rating {RATING_CLASSES.get(rating, "neutral")}">'
        f'{_esc(rating)}</div>'
    )


def detail_header(title, meta, rating):

    _render(
        '<div class="ba-detail-head">'
        f'<span class="ba-detail-title">{_esc(title)}</span>'
        f'{rating_badge(rating)}'
        f'<span class="ba-detail-meta">{_esc(meta)}</span>'
        '</div>'
    )


def factor_grades(factors):

    parts = []

    for key, label, description in FACTOR_LABELS:

        grade = (
            factors.get(key) or {}
        ).get("grade")

        if grade:
            grade_class = (
                grade[0].lower()
                if grade[0] in "ABC"
                else "d"
            )

        else:
            grade_class = "none"

        parts.append(
            '<div class="ba-factor">'
            f'<div class="ba-factor-name">{label}</div>'
            f'<div class="ba-factor-grade {grade_class}">{_esc(grade or "–")}</div>'
            f'<div class="ba-factor-desc">{_esc(description)}</div>'
            '</div>'
        )

    _render(
        f'<div class="ba-factors">{"".join(parts)}</div>'
    )
