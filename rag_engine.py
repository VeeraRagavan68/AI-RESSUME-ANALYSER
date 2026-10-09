"""
RAG Engine Module
Builds vector store from job role documents and retrieves relevant skills.
"""
import json
import numpy as np
from typing import List, Dict, Tuple
from pathlib import Path
import re


class SimpleEmbedding:
    """Simple TF-IDF style embedding for demo (replace with real embeddings in production)."""

    def __init__(self):
        self.vocab = {}
        self.idf = {}

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization."""
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        tokens = text.split()
        return [t for t in tokens if len(t) > 2]

    def fit(self, documents: List[str]):
        """Build vocabulary and IDF from documents."""
        # Build vocab
        all_tokens = []
        doc_tokens = []
        for doc in documents:
            tokens = self._tokenize(doc)
            doc_tokens.append(tokens)
            all_tokens.extend(tokens)

        unique_tokens = list(set(all_tokens))
        self.vocab = {token: idx for idx, token in enumerate(unique_tokens)}

        # Compute IDF
        N = len(documents)
        for token in unique_tokens:
            df = sum(1 for tokens in doc_tokens if token in tokens)
            self.idf[token] = np.log(N / (df + 1)) + 1

    def embed(self, text: str) -> np.ndarray:
        """Embed text into vector."""
        tokens = self._tokenize(text)
        vec = np.zeros(len(self.vocab))

        for token in tokens:
            if token in self.vocab:
                idx = self.vocab[token]
                vec[idx] += self.idf.get(token, 1)

        # L2 normalize
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec


class RAGEngine:
    """Retrieval-Augmented Generation for job role skill matching."""

    def __init__(self, job_roles_path: str = "data/job_roles.json"):
        self.job_roles_path = job_roles_path
        self.job_roles = {}
        self.documents = []
        self.doc_metadata = []
        self.embedder = SimpleEmbedding()
        self.embeddings = None
        self._load_data()
        self._build_index()

    def _load_data(self):
        """Load job role data."""
        path = Path(self.job_roles_path)
        if path.exists():
            with open(path, "r") as f:
                self.job_roles = json.load(f)
        else:
            # Fallback empty data
            self.job_roles = {}

    def _build_index(self):
        """Build vector index from job role documents."""
        self.documents = []
        self.doc_metadata = []

        for role_key, role_data in self.job_roles.items():
            # Create rich documents for each skill
            for skill in role_data.get("required_skills", []):
                doc_text = f"{role_data['title']} {role_data['level']} {skill['name']} {skill['category']} {skill['priority']} {skill['proficiency']}"
                self.documents.append(doc_text)
                self.doc_metadata.append({
                    "role_key": role_key,
                    "role_title": role_data["title"],
                    "skill": skill,
                })

            # Also index the role description
            desc_doc = f"{role_data['title']} {role_data['description']}"
            self.documents.append(desc_doc)
            self.doc_metadata.append({
                "role_key": role_key,
                "role_title": role_data["title"],
                "skill": None,
                "description": True
            })

        # Fit embedder and compute embeddings
        if self.documents:
            self.embedder.fit(self.documents)
            self.embeddings = np.array([self.embedder.embed(doc) for doc in self.documents])

    def retrieve(self, query: str, top_k: int = 15) -> List[Dict]:
        """Retrieve top-k relevant skills for a query."""
        if self.embeddings is None or len(self.embeddings) == 0:
            return []

        query_vec = self.embedder.embed(query)

        # Cosine similarity
        similarities = self.embeddings @ query_vec

        # Get top-k
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        seen_skills = set()
        for idx in top_indices:
            meta = self.doc_metadata[idx]
            sim = float(similarities[idx])

            if meta.get("skill"):
                skill_name = meta["skill"]["name"]
                if skill_name not in seen_skills:
                    seen_skills.add(skill_name)
                    results.append({
                        "role": meta["role_title"],
                        "role_key": meta["role_key"],
                        "skill": meta["skill"],
                        "similarity": round(sim, 3)
                    })
            else:
                results.append({
                    "role": meta["role_title"],
                    "role_key": meta["role_key"],
                    "description": meta.get("description", False),
                    "similarity": round(sim, 3)
                })

        return results

    def get_role_skills(self, role_key: str) -> List[Dict]:
        """Get all required skills for a specific role."""
        role = self.job_roles.get(role_key, {})
        return role.get("required_skills", [])

    def get_role_info(self, role_key: str) -> Dict:
        """Get role information."""
        return self.job_roles.get(role_key, {})

    def list_roles(self) -> List[Dict]:
        """List all available roles."""
        return [
            {"key": k, "title": v["title"], "level": v["level"]}
            for k, v in self.job_roles.items()
        ]
