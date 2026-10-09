"""
SkillSync AI — veera ragavan — Smart Resume Gap Analyzer
Streamlit Application
"""
import streamlit as st
import json
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

from resume_parser import ResumeParser
from skill_extractor import SkillExtractor
from rag_engine import RAGEngine
from gap_analyzer import GapAnalyzer, ReportGenerator


st.set_page_config(
    page_title="SkillSync AI — veera ragavan",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    .skill-tag {
        display: inline-block;
        background: #dbeafe;
        color: #1e40af;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        margin: 2px;
        font-weight: 500;
    }
    .gap-must {
        border-left: 4px solid #ef4444;
        padding-left: 12px;
        margin: 8px 0;
        background: #fef2f2;
        padding: 12px;
        border-radius: 8px;
    }
    .gap-should {
        border-left: 4px solid #f59e0b;
        padding-left: 12px;
        margin: 8px 0;
        background: #fffbeb;
        padding: 12px;
        border-radius: 8px;
    }
    .gap-nice {
        border-left: 4px solid #10b981;
        padding-left: 12px;
        margin: 8px 0;
        background: #ecfdf5;
        padding: 12px;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_components():
    rag = RAGEngine("data/job_roles.json")
    analyzer = GapAnalyzer(rag, "data/courses.json")
    return rag, analyzer

rag, analyzer = load_components()

with st.sidebar:
    st.markdown("# 🎯 SkillSync AI — veera ragavan")
    st.markdown("**AI-Powered Resume Gap Analyzer**")
    st.markdown("---")
    st.markdown("### How it works")
    st.markdown("""
    1. 📄 Upload your resume
    2. 🎯 Select target role
    3. 🔍 AI extracts your skills
    4. 📊 RAG compares against job requirements
    5. 🎓 Get personalized learning path
    """)
    st.markdown("---")
    st.markdown("Built by veera ragavan ❤️")

st.markdown('<div class="main-header">🎯 SkillSync AI — veera ragavan</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Upload your resume, choose a target role, and get an AI-powered skill gap analysis with a personalized learning roadmap.</div>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📄 Step 1: Upload Resume")
    uploaded_file = st.file_uploader(
        "Upload PDF, DOCX, or TXT",
        type=["pdf", "docx", "txt"],
        help="Your resume will be parsed locally. No data leaves your machine."
    )

    st.markdown("### 🎯 Step 2: Select Target Role")
    roles = rag.list_roles()
    role_options = {f"{r['title']} ({r['level']})": r['key'] for r in roles}
    selected_role_label = st.selectbox("Choose your target position", list(role_options.keys()))
    selected_role_key = role_options[selected_role_label]

with col2:
    st.markdown("### ℹ️ Target Role Info")
    role_info = rag.get_role_info(selected_role_key)
    st.info(f"**{role_info['title']}** — {role_info['description']}")
    skills_preview = role_info.get("required_skills", [])[:5]
    st.markdown("**Top required skills:**")
    for sk in skills_preview:
        st.markdown(f"- {sk['name']} ({sk['priority']})")

analyze_clicked = st.button("🔍 Analyze My Resume", type="primary", use_container_width=True)

if analyze_clicked and uploaded_file is not None:
    with st.spinner("🤖 AI is analyzing your resume..."):
        try:
            parser = ResumeParser()
            resume_text = parser.parse_bytes(uploaded_file.read(), uploaded_file.name)

            extractor = SkillExtractor()
            extracted_skills = extractor.extract(resume_text)

            result = analyzer.analyze(extracted_skills, selected_role_key)

            st.success("Analysis complete!")

            st.markdown("---")
            st.markdown("## 📊 Analysis Results")

            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric("Match Score", f"{result.match_score}%")
            with m2:
                st.metric("Readiness", result.readiness_level)
            with m3:
                st.metric("Skills Found", len(extracted_skills))
            with m4:
                st.metric("Gaps Found", len(result.gaps))

            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=result.match_score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Role Match Score"},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "#3b82f6"},
                    'steps': [
                        {'range': [0, 50], 'color': "#fef2f2"},
                        {'range': [50, 70], 'color': "#fffbeb"},
                        {'range': [70, 85], 'color': "#ecfdf5"},
                        {'range': [85, 100], 'color': "#dbeafe"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 70
                    }
                }
            ))
            fig_gauge.update_layout(height=300)
            st.plotly_chart(fig_gauge, use_container_width=True)

            left, right = st.columns([1, 1])

            with left:
                st.markdown("### ✅ Your Detected Skills")
                if extracted_skills:
                    for skill in extracted_skills:
                        st.markdown(f'<span class="skill-tag">{skill.name}</span>', unsafe_allow_html=True)
                else:
                    st.warning("No specific skills detected. Try a more detailed resume.")

                st.markdown("---")
                st.markdown("### 💪 Strengths")
                if result.strengths:
                    for s in result.strengths:
                        st.markdown(f"✅ **{s['skill']}** ({s['category']})")
                else:
                    st.info("No strong matches found for this role yet.")

            with right:
                st.markdown("### 📉 Skill Gaps")
                st.caption(f"Estimated timeline to close gaps: **{result.timeline_weeks} weeks**")

                must_gaps = [g for g in result.gaps if g.priority == "must"]
                should_gaps = [g for g in result.gaps if g.priority == "should"]
                nice_gaps = [g for g in result.gaps if g.priority == "nice"]

                if must_gaps:
                    st.markdown("**🔴 Must-Have Gaps**")
                    for g in must_gaps:
                        st.markdown(f'<div class="gap-must"><b>{g.skill_name}</b> ({g.category})<br/>Target: {g.proficiency_required}</div>', unsafe_allow_html=True)

                if should_gaps:
                    st.markdown("**🟡 Should-Have Gaps**")
                    for g in should_gaps:
                        st.markdown(f'<div class="gap-should"><b>{g.skill_name}</b> ({g.category})<br/>Target: {g.proficiency_required}</div>', unsafe_allow_html=True)

                if nice_gaps:
                    with st.expander("🟢 Nice-to-Have Gaps"):
                        for g in nice_gaps:
                            st.markdown(f'<div class="gap-nice"><b>{g.skill_name}</b> ({g.category})</div>', unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("## 🎓 Personalized Learning Path")
            st.caption("Top-priority courses to close your skill gaps")

            for i, rec in enumerate(result.recommendations[:6], 1):
                with st.container():
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        priority_color = {"must": "🔴", "should": "🟡", "nice": "🟢"}.get(rec['priority'], "⚪")
                        st.markdown(f"### {priority_color} {i}. {rec['skill']}")
                        st.markdown(f"**Category:** {rec['category']} | **Status:** {rec['status']} | **Target:** {rec['proficiency_target']}")
                        st.markdown(f"⏱️ Estimated time: {rec['estimated_time']}")
                    with col_b:
                        if rec['courses']:
                            st.markdown("**Recommended:**")
                            for c in rec['courses'][:2]:
                                st.markdown(f"[{c['title']}]({c['url']})")
                                st.caption(f"{c['provider']} • {c['type']}")
                        else:
                            st.info("Search online for courses on this topic")
                    st.markdown("---")

            st.markdown("## 📈 Gap Analysis by Category")
            category_data = {}
            for g in result.gaps:
                cat = g.category
                if cat not in category_data:
                    category_data[cat] = {"missing": 0, "partial": 0}
                category_data[cat][g.status] += 1

            if category_data:
                cats = list(category_data.keys())
                missing = [category_data[c]["missing"] for c in cats]
                partial = [category_data[c]["partial"] for c in cats]

                fig_bar = go.Figure(data=[
                    go.Bar(name='Missing', x=cats, y=missing, marker_color='#ef4444'),
                    go.Bar(name='Partial', x=cats, y=partial, marker_color='#f59e0b')
                ])
                fig_bar.update_layout(barmode='stack', height=400, xaxis_title="Category", yaxis_title="Skill Gaps")
                st.plotly_chart(fig_bar, use_container_width=True)

            st.markdown("---")
            report_md = ReportGenerator.generate_markdown(result)
            report_json = ReportGenerator.generate_json(result)

            c1, c2 = st.columns(2)
            with c1:
                st.download_button(
                    "📥 Download Markdown Report",
                    report_md,
                    file_name=f"skillsync_report_{selected_role_key}.md",
                    mime="text/markdown"
                )
            with c2:
                st.download_button(
                    "📥 Download JSON Report",
                    json.dumps(report_json, indent=2),
                    file_name=f"skillsync_report_{selected_role_key}.json",
                    mime="application/json"
                )

        except Exception as e:
            st.error(f"Error during analysis: {str(e)}")
            st.info("Make sure your resume file is readable and contains text (not just images).")

elif analyze_clicked and uploaded_file is None:
    st.warning("Please upload a resume file first!")

st.markdown("---")
st.caption("SkillSync AI — veera ragavan • Built with Streamlit, Plotly, and RAG • For educational/workshop use")
