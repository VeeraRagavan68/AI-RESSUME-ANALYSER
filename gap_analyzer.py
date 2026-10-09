"""
Gap Analyzer Module
Compares extracted resume skills against target role requirements.
Generates gap analysis, scoring, and learning path recommendations.
"""
import json
from typing import List, Dict, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SkillGap:
    skill_name: str
    category: str
    priority: str
    proficiency_required: str
    status: str
    confidence: float


@dataclass
class AnalysisResult:
    target_role: str
    role_level: str
    match_score: float
    readiness_level: str
    gaps: List[SkillGap]
    strengths: List[Dict]
    recommendations: List[Dict]
    timeline_weeks: int


class GapAnalyzer:
    """Analyze skill gaps between resume and target role."""

    def __init__(self, rag_engine, courses_path: str = "data/courses.json"):
        self.rag = rag_engine
        self.courses = self._load_courses(courses_path)

    def _load_courses(self, path: str) -> Dict[str, List[Dict]]:
        """Load and index courses by skill."""
        courses_by_skill = {}
        p = Path(path)
        if p.exists():
            with open(path, "r") as f:
                courses = json.load(f)
            for c in courses:
                skill = c["skill"]
                if skill not in courses_by_skill:
                    courses_by_skill[skill] = []
                courses_by_skill[skill].append(c)
        return courses_by_skill

    def analyze(self, resume_skills: List, target_role_key: str) -> AnalysisResult:
        """Perform full gap analysis."""
        role_info = self.rag.get_role_info(target_role_key)
        required_skills = self.rag.get_role_skills(target_role_key)
        resume_skill_names = {s.name.lower() for s in resume_skills}

        gaps = []
        strengths = []
        total_weight = 0
        earned_weight = 0

        for req in required_skills:
            skill_name = req["name"]
            skill_key = skill_name.lower()
            weight = self._priority_weight(req["priority"])
            total_weight += weight

            match_score = self._fuzzy_match(skill_key, resume_skill_names)

            if match_score >= 0.8:
                status = "present"
                earned_weight += weight
                strengths.append({
                    "skill": skill_name,
                    "category": req["category"],
                    "priority": req["priority"],
                    "proficiency": req["proficiency"]
                })
            elif match_score >= 0.4:
                status = "partial"
                earned_weight += weight * 0.3
                gaps.append(SkillGap(
                    skill_name=skill_name,
                    category=req["category"],
                    priority=req["priority"],
                    proficiency_required=req["proficiency"],
                    status=status,
                    confidence=match_score
                ))
            else:
                status = "missing"
                gaps.append(SkillGap(
                    skill_name=skill_name,
                    category=req["category"],
                    priority=req["priority"],
                    proficiency_required=req["proficiency"],
                    status=status,
                    confidence=0.0
                ))

        match_score = (earned_weight / total_weight * 100) if total_weight > 0 else 0
        match_score = round(min(match_score, 100), 1)
        readiness = self._readiness_level(match_score, gaps)
        recommendations = self._generate_recommendations(gaps, target_role_key)
        timeline = self._estimate_timeline(gaps)

        return AnalysisResult(
            target_role=role_info.get("title", target_role_key),
            role_level=role_info.get("level", "Mid-Level"),
            match_score=match_score,
            readiness_level=readiness,
            gaps=gaps,
            strengths=strengths,
            recommendations=recommendations,
            timeline_weeks=timeline
        )

    def _priority_weight(self, priority: str) -> float:
        weights = {"must": 3.0, "should": 1.5, "nice": 0.5}
        return weights.get(priority, 1.0)

    def _fuzzy_match(self, skill_key: str, resume_skills: set) -> float:
        if skill_key in resume_skills:
            return 1.0
        for rs in resume_skills:
            if skill_key in rs or rs in skill_key:
                return 0.6
            skill_words = set(skill_key.split())
            resume_words = set(rs.split())
            if skill_words and resume_words:
                overlap = len(skill_words & resume_words) / max(len(skill_words), len(resume_words))
                if overlap >= 0.5:
                    return 0.5
        return 0.0

    def _readiness_level(self, score: float, gaps: List[SkillGap]) -> str:
        must_missing = sum(1 for g in gaps if g.priority == "must" and g.status == "missing")
        if score >= 85 and must_missing == 0:
            return "Strong Fit"
        elif score >= 70 and must_missing <= 1:
            return "Ready"
        elif score >= 50:
            return "Junior Ready"
        else:
            return "Not Ready"

    def _generate_recommendations(self, gaps: List[SkillGap], role_key: str) -> List[Dict]:
        sorted_gaps = sorted(gaps, key=lambda g: (
            {"must": 0, "should": 1, "nice": 2}.get(g.priority, 3),
            {"missing": 0, "partial": 1}.get(g.status, 2)
        ))

        recommendations = []
        for gap in sorted_gaps[:10]:
            courses = self.courses.get(gap.skill_name, [])
            if not courses:
                for skill_name, course_list in self.courses.items():
                    if gap.skill_name.lower() in skill_name.lower() or skill_name.lower() in gap.skill_name.lower():
                        courses = course_list
                        break

            rec = {
                "skill": gap.skill_name,
                "category": gap.category,
                "priority": gap.priority,
                "status": gap.status,
                "proficiency_target": gap.proficiency_required,
                "courses": courses[:3] if courses else [],
                "estimated_time": self._skill_time_estimate(gap)
            }
            recommendations.append(rec)

        return recommendations

    def _skill_time_estimate(self, gap: SkillGap) -> str:
        estimates = {
            "beginner": "2-4 weeks",
            "intermediate": "4-8 weeks",
            "advanced": "8-16 weeks"
        }
        base = estimates.get(gap.proficiency_required, "4-6 weeks")
        if gap.status == "partial":
            return f"~{base.split('-')[0]} weeks (partial knowledge)"
        return base

    def _estimate_timeline(self, gaps: List[SkillGap]) -> int:
        must_missing = [g for g in gaps if g.priority == "must" and g.status == "missing"]
        should_missing = [g for g in gaps if g.priority == "should" and g.status == "missing"]
        weeks = len(must_missing) * 3 + len(should_missing) * 2
        return max(weeks, 4)


class ReportGenerator:
    """Generate structured analysis reports."""

    @staticmethod
    def generate_markdown(result: AnalysisResult) -> str:
        lines = [
            "# SkillSync Analysis Report — By Farise aml",
            "",
            f"## Target Role: {result.target_role} ({result.role_level})",
            "",
            f"**Match Score:** {result.match_score}/100",
            "",
            f"**Readiness:** {result.readiness_level}",
            "",
            f"**Estimated Timeline:** {result.timeline_weeks} weeks",
            "",
            "---",
            "",
            f"## Strengths ({len(result.strengths)} skills)",
            "",
        ]
        for s in result.strengths:
            lines.append(f"- **{s['skill']}** ({s['category']}) — {s['proficiency']}")

        lines.extend([
            "",
            f"## Skill Gaps ({len(result.gaps)} gaps)",
            "",
            "| Skill | Category | Priority | Status | Target Level |",
            "|-------|----------|----------|--------|--------------|",
        ])
        for g in result.gaps:
            status_emoji = "🔴" if g.status == "missing" else "🟡"
            lines.append(f"| {g.skill_name} | {g.category} | {g.priority} | {status_emoji} {g.status} | {g.proficiency_required} |")

        lines.extend(["", "## Recommended Learning Path", ""])
        for i, rec in enumerate(result.recommendations, 1):
            lines.append(f"### {i}. {rec['skill']} ({rec['priority']} priority)")
            lines.append(f"- **Status:** {rec['status']}")
            lines.append(f"- **Target:** {rec['proficiency_target']}")
            lines.append(f"- **Estimated Time:** {rec['estimated_time']}")
            if rec['courses']:
                lines.append("- **Top Resources:**")
                for c in rec['courses'][:2]:
                    lines.append(f"  - [{c['title']}]({c['url']}) — {c['provider']} ({c['type']})")
            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def generate_json(result: AnalysisResult) -> Dict:
        return {
            "target_role": result.target_role,
            "role_level": result.role_level,
            "match_score": result.match_score,
            "readiness_level": result.readiness_level,
            "timeline_weeks": result.timeline_weeks,
            "strengths": result.strengths,
            "gaps": [
                {
                    "skill": g.skill_name,
                    "category": g.category,
                    "priority": g.priority,
                    "status": g.status,
                    "proficiency_required": g.proficiency_required
                }
                for g in result.gaps
            ],
            "recommendations": result.recommendations
        }
