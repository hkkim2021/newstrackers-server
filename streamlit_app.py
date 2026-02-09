import json
import logging
import uuid
from collections import Counter, defaultdict

import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from matplotlib import font_manager
from wordcloud import WordCloud

logging.basicConfig(level=logging.INFO)

# 한글 폰트 설정
def get_korean_font_path():
    """시스템에서 한글 폰트를 찾는다."""
    for font in font_manager.fontManager.ttflist:
        if any(name in font.name for name in ["AppleGothic", "Malgun Gothic", "NanumGothic", "Noto Sans CJK"]):
            return font.fname
    return None

KOREAN_FONT = get_korean_font_path()
if KOREAN_FONT:
    plt.rcParams["font.family"] = font_manager.FontProperties(fname=KOREAN_FONT).get_name()
    plt.rcParams["axes.unicode_minus"] = False


def run_pipeline(uploaded_file):
    """Node1→2→3→4 전체 파이프라인 실행."""
    from app.core.database import SessionLocal
    from app.agents.graphs.pipeline import run_full_pipeline

    file_bytes = uploaded_file.read()

    db = SessionLocal()
    try:
        with st.spinner("Node1→2→3→4 파이프라인 실행 중..."):
            result = run_full_pipeline(file_bytes, uploaded_file.name, db)
        return result
    except ValueError as e:
        st.error(str(e))
        return None
    finally:
        db.close()


def render_profile(profile: dict):
    """Node1 프로필 결과를 표시한다."""
    st.subheader("Node1: 프로필 분석 결과")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("희망 직무", profile.get("target_position", "-"))
        st.metric("목표 산업", profile.get("target_industry", "-"))
    with col2:
        companies = profile.get("interested_companies", [])
        st.metric("관심 회사", ", ".join(companies) if companies else "없음")
        st.metric("분야", ", ".join(profile.get("fields", [])))

    # 기술 스택
    tech_stack = profile.get("tech_stack", {})
    if tech_stack:
        st.markdown("**기술 스택**")
        for category, techs in tech_stack.items():
            if techs:
                st.markdown(f"- `{category}`: {', '.join(techs)}")


def render_keyword_wordcloud(profile: dict):
    """키워드 워드클라우드를 표시한다."""
    keywords = profile.get("keywords", [])
    if not keywords:
        return

    st.subheader("키워드 워드클라우드")
    word_freq = Counter(keywords)

    font_path = KOREAN_FONT
    wc = WordCloud(
        width=800,
        height=400,
        background_color="white",
        font_path=font_path,
        colormap="viridis",
    ).generate_from_frequencies(word_freq)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)
    plt.close(fig)


def render_pipeline_summary(result: dict):
    """파이프라인 요약 메트릭을 표시한다."""
    st.subheader("파이프라인 요약")
    summary = result.get("pipeline_summary", {})

    col1, col2, col3 = st.columns(3)
    col1.metric("Node2: 1차 필터링", f"{summary.get('node2_filtered', 0)}건")
    col2.metric("Node3: AI 점수 통과", f"{summary.get('node3_scored', 0)}건")
    col3.metric("최소 점수 기준", f"{summary.get('min_score', 70)}점")


def render_grouped_articles(grouped: dict):
    """그룹핑된 뉴스를 차트로 표시한다."""
    if not grouped:
        st.info("그룹핑된 뉴스가 없습니다.")
        return

    st.subheader("Node3: 카테고리별 뉴스 분포")

    # 카테고리별 뉴스 수 바차트
    categories = []
    counts = []
    for cat, data in grouped.items():
        categories.append(cat)
        counts.append(data.get("count", 0))

    fig = px.bar(
        x=categories, y=counts,
        labels={"x": "카테고리", "y": "뉴스 수"},
        color=counts,
        color_continuous_scale="Blues",
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    # 회사별 뉴스 수 (전체 합산)
    company_counts = Counter()
    for data in grouped.values():
        for company, articles in data.get("companies", {}).items():
            company_counts[company] += len(articles)

    if company_counts:
        st.subheader("회사별 뉴스 분포")
        top_companies = company_counts.most_common(10)
        fig2 = px.pie(
            names=[c[0] for c in top_companies],
            values=[c[1] for c in top_companies],
        )
        st.plotly_chart(fig2, use_container_width=True)

    # 카테고리별 상세
    for cat, data in grouped.items():
        with st.expander(f"{cat} ({data.get('count', 0)}건)"):
            for company, articles in data.get("companies", {}).items():
                st.markdown(f"**{company}**")
                for a in articles:
                    score = a.get("score", 0)
                    title = a.get("title", "")
                    st.markdown(f"- [{score}점] {title}")


def render_score_distribution(grouped: dict):
    """관련성 점수 분포를 표시한다."""
    all_scores = []
    for data in grouped.values():
        for articles in data.get("companies", {}).values():
            for a in articles:
                all_scores.append(a.get("score", 0))

    if not all_scores:
        return

    st.subheader("관련성 점수 분포")
    fig = px.histogram(
        x=all_scores,
        nbins=10,
        labels={"x": "관련성 점수", "y": "뉴스 수"},
        color_discrete_sequence=["#636EFA"],
    )
    st.plotly_chart(fig, use_container_width=True)


def render_report(report: str):
    """마크다운 리포트를 표시한다."""
    st.subheader("Node4: 면접 준비 리포트")
    st.markdown(report)


# --- Streamlit App ---

st.set_page_config(page_title="면접 뉴스 트래커", layout="wide")
st.title("면접 뉴스 트래커")
st.caption("자소서 PDF를 업로드하면 맞춤형 면접 준비 리포트를 생성합니다.")

uploaded_file = st.file_uploader("자소서 PDF 업로드", type=["pdf"])

if uploaded_file:
    if st.button("분석 시작", type="primary"):
        result = run_pipeline(uploaded_file)

        if result:
            st.success(f"분석 완료! (resume_id: {result['resume_id']})")
            st.divider()

            # Node1: 프로필
            render_profile(result["profile"])
            render_keyword_wordcloud(result["profile"])

            st.divider()

            # 파이프라인 요약
            render_pipeline_summary(result)

            # Node3: 그룹핑 시각화
            grouped = result.get("grouped_articles", {})
            render_grouped_articles(grouped)
            render_score_distribution(grouped)

            st.divider()

            # Node4: 리포트
            render_report(result.get("report", "리포트 생성에 실패했습니다."))
