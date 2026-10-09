"""
Skill Extractor Module
Extracts skills from resume text using keyword matching + LLM fallback.
"""
import re
import json
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass


@dataclass
class ExtractedSkill:
    name: str
    category: str
    confidence: float  # 0.0 to 1.0
    evidence: str  # sentence from resume


class SkillExtractor:
    """Extract skills from resume text."""

    def __init__(self):
        self.skill_patterns = self._build_skill_patterns()

    def _build_skill_patterns(self) -> Dict[str, Dict]:
        """Build comprehensive skill pattern database."""
        return {
            # Languages
            "python": {"category": "Language", "aliases": ["python", "py", "python3"]},
            "javascript": {"category": "Language", "aliases": ["javascript", "js", "es6", "ecmascript"]},
            "typescript": {"category": "Language", "aliases": ["typescript", "ts"]},
            "java": {"category": "Language", "aliases": ["java", "javase", "java ee"]},
            "c++": {"category": "Language", "aliases": ["c++", "cpp", "c plus plus"]},
            "c#": {"category": "Language", "aliases": ["c#", "csharp", ".net"]},
            "go": {"category": "Language", "aliases": ["go", "golang"]},
            "rust": {"category": "Language", "aliases": ["rust", "rustlang"]},
            "ruby": {"category": "Language", "aliases": ["ruby", "ruby on rails", "rails"]},
            "php": {"category": "Language", "aliases": ["php", "php8"]},
            "swift": {"category": "Language", "aliases": ["swift", "swiftui"]},
            "kotlin": {"category": "Language", "aliases": ["kotlin"]},
            "scala": {"category": "Language", "aliases": ["scala"]},
            "r": {"category": "Language", "aliases": ["r programming", "r language"]},
            "bash": {"category": "Language", "aliases": ["bash", "shell scripting", "shell script"]},
            "sql": {"category": "Language", "aliases": ["sql", "mysql", "postgresql", "sqlite"]},

            # Web/Frameworks
            "react": {"category": "Frontend", "aliases": ["react", "react.js", "reactjs"]},
            "vue": {"category": "Frontend", "aliases": ["vue", "vue.js", "vuejs"]},
            "angular": {"category": "Frontend", "aliases": ["angular", "angularjs"]},
            "next.js": {"category": "Frontend", "aliases": ["next.js", "nextjs", "next"]},
            "node.js": {"category": "Backend", "aliases": ["node.js", "nodejs", "node"]},
            "django": {"category": "Backend", "aliases": ["django"]},
            "flask": {"category": "Backend", "aliases": ["flask"]},
            "fastapi": {"category": "Backend", "aliases": ["fastapi", "fast api"]},
            "spring boot": {"category": "Backend", "aliases": ["spring boot", "springboot"]},
            "express": {"category": "Backend", "aliases": ["express", "express.js"]},
            "graphql": {"category": "Backend", "aliases": ["graphql", "graph ql"]},
            "rest api": {"category": "Backend", "aliases": ["rest", "restful", "rest api", "restful api"]},

            # Data/ML
            "pandas": {"category": "Data", "aliases": ["pandas"]},
            "numpy": {"category": "Data", "aliases": ["numpy"]},
            "scikit-learn": {"category": "ML", "aliases": ["scikit-learn", "sklearn", "scikitlearn"]},
            "tensorflow": {"category": "ML", "aliases": ["tensorflow", "tf"]},
            "pytorch": {"category": "ML", "aliases": ["pytorch", "torch"]},
            "keras": {"category": "ML", "aliases": ["keras"]},
            "machine learning": {"category": "ML", "aliases": ["machine learning", "ml", "machine-learning"]},
            "deep learning": {"category": "ML", "aliases": ["deep learning", "dl", "neural networks", "neural network"]},
            "nlp": {"category": "ML", "aliases": ["nlp", "natural language processing", "text mining"]},
            "computer vision": {"category": "ML", "aliases": ["computer vision", "cv", "image processing"]},
            "data visualization": {"category": "Data", "aliases": ["data visualization", "data viz", "matplotlib", "seaborn", "plotly", "tableau", "power bi"]},
            "statistics": {"category": "Math", "aliases": ["statistics", "statistical analysis", "probability"]},
            "feature engineering": {"category": "ML", "aliases": ["feature engineering", "feature extraction"]},
            "a/b testing": {"category": "Analytics", "aliases": ["a/b testing", "ab testing", "split testing", "experimentation"]},
            "big data": {"category": "Data", "aliases": ["big data", "spark", "hadoop", "apache spark"]},

            # DevOps/Cloud
            "docker": {"category": "DevOps", "aliases": ["docker", "containerization", "containers"]},
            "kubernetes": {"category": "DevOps", "aliases": ["kubernetes", "k8s", "kubectl"]},
            "aws": {"category": "Cloud", "aliases": ["aws", "amazon web services", "ec2", "s3", "lambda"]},
            "gcp": {"category": "Cloud", "aliases": ["gcp", "google cloud", "google cloud platform"]},
            "azure": {"category": "Cloud", "aliases": ["azure", "microsoft azure"]},
            "terraform": {"category": "DevOps", "aliases": ["terraform", "iac", "infrastructure as code"]},
            "ansible": {"category": "DevOps", "aliases": ["ansible"]},
            "jenkins": {"category": "DevOps", "aliases": ["jenkins", "ci/cd", "cicd", "continuous integration"]},
            "github actions": {"category": "DevOps", "aliases": ["github actions", "gitlab ci"]},
            "prometheus": {"category": "DevOps", "aliases": ["prometheus", "grafana", "monitoring"]},
            "linux": {"category": "Systems", "aliases": ["linux", "unix", "ubuntu", "centos", "debian"]},
            "nginx": {"category": "DevOps", "aliases": ["nginx"]},
            "git": {"category": "DevOps", "aliases": ["git", "version control"]},

            # Architecture
            "microservices": {"category": "Architecture", "aliases": ["microservices", "microservice", "micro-services"]},
            "system design": {"category": "Architecture", "aliases": ["system design", "distributed systems", "scalability", "high availability"]},
            "serverless": {"category": "Architecture", "aliases": ["serverless", "faas"]},
            "event-driven": {"category": "Architecture", "aliases": ["event-driven", "event driven", "message queues", "kafka", "rabbitmq"]},

            # Security
            "oauth": {"category": "Security", "aliases": ["oauth", "jwt", "authentication", "authorization", "sso"]},
            "cybersecurity": {"category": "Security", "aliases": ["cybersecurity", "security", "penetration testing", "encryption"]},

            # Mobile
            "flutter": {"category": "Mobile", "aliases": ["flutter", "dart"]},
            "react native": {"category": "Mobile", "aliases": ["react native", "reactnative"]},
            "android": {"category": "Mobile", "aliases": ["android", "android development"]},
            "ios": {"category": "Mobile", "aliases": ["ios", "ios development", "objective-c"]},

            # PM/Soft Skills
            "product management": {"category": "Strategy", "aliases": ["product management", "product manager", "pm"]},
            "agile": {"category": "Process", "aliases": ["agile", "scrum", "kanban", "sprint"]},
            "user research": {"category": "UX", "aliases": ["user research", "ux research", "user testing"]},
            "roadmapping": {"category": "Strategy", "aliases": ["roadmap", "roadmapping", "product strategy"]},
            "stakeholder management": {"category": "Leadership", "aliases": ["stakeholder management", "cross-functional"]},
            "data analytics": {"category": "Analytics", "aliases": ["data analytics", "business intelligence", "bi"]},

            # Testing
            "unit testing": {"category": "Quality", "aliases": ["unit testing", "jest", "pytest", "mocha", "junit"]},
            "integration testing": {"category": "Quality", "aliases": ["integration testing", "e2e testing", "selenium", "cypress"]},
            "test-driven development": {"category": "Quality", "aliases": ["tdd", "test-driven development", "test driven"]},

            # Databases
            "mongodb": {"category": "Data", "aliases": ["mongodb", "mongo", "nosql"]},
            "redis": {"category": "Data", "aliases": ["redis", "caching"]},
            "elasticsearch": {"category": "Data", "aliases": ["elasticsearch", "elk stack", "elastic search"]},
            "postgresql": {"category": "Data", "aliases": ["postgresql", "postgres"]},
            "mysql": {"category": "Data", "aliases": ["mysql", "mariadb"]},
        }

    def extract(self, resume_text: str) -> List[ExtractedSkill]:
        """Extract skills from resume text."""
        text_lower = resume_text.lower()
        sentences = re.split(r'[.!?\n]+', resume_text)

        found_skills = []
        found_names = set()

        for skill_key, skill_info in self.skill_patterns.items():
            for alias in skill_info["aliases"]:
                # Word boundary matching for better accuracy
                pattern = r'(?:^|[^\w])' + re.escape(alias) + r'(?:[^\w]|$)'
                matches = list(re.finditer(pattern, text_lower))

                if matches:
                    if skill_key not in found_names:
                        # Find the best evidence sentence
                        best_evidence = self._find_evidence(sentences, alias)
                        confidence = min(0.5 + 0.1 * len(matches), 0.95)

                        found_skills.append(ExtractedSkill(
                            name=skill_key,
                            category=skill_info["category"],
                            confidence=confidence,
                            evidence=best_evidence
                        ))
                        found_names.add(skill_key)
                    break  # Found one alias, skip others

        # Sort by confidence
        found_skills.sort(key=lambda x: x.confidence, reverse=True)
        return found_skills

    def _find_evidence(self, sentences: List[str], keyword: str) -> str:
        """Find the sentence containing the keyword."""
        keyword_lower = keyword.lower()
        for sentence in sentences:
            if keyword_lower in sentence.lower() and len(sentence) > 10:
                return sentence.strip()[:200]
        return "Found in resume text"

    def get_skill_names(self, skills: List[ExtractedSkill]) -> Set[str]:
        """Get just the skill names."""
        return {s.name for s in skills}
