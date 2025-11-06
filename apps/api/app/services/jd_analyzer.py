"""Job Description analysis service"""

import re
from typing import Any

import spacy
from openai import AsyncOpenAI

from app.config import settings
from app.services.types import JDSpan, Skill, CourseworkItem

# Initialize spaCy model (load once)
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # Fallback if model not loaded
    nlp = None

# Initialize OpenAI client
openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def analyze_jd(jd_text: str) -> tuple[JDSpan, list[Skill], list[CourseworkItem]]:
    """
    Analyze job description and extract skills.
    
    Returns:
        - JDSpan with character index spans
        - List of skills with scores
        - List of coursework items with scores
    """
    # Step 1: Segment JD using regex/heuristic
    spans = segment_jd_regex(jd_text)
    
    # Step 2: If regex coverage < 70%, use LLM fallback
    coverage = calculate_coverage(spans, len(jd_text))
    if coverage < 0.7:
        spans = await segment_jd_llm(jd_text)
    
    # Step 3: Extract skills using spaCy
    skills = extract_skills_with_spacy(jd_text, spans)
    
    # Step 4: Extract coursework (if mentioned)
    coursework = extract_coursework(jd_text)
    
    # Step 5: Score and sort skills
    skills = score_and_sort_skills(skills, spans, jd_text)
    
    # Step 6: Cap coursework to top 6
    coursework = sorted(coursework, key=lambda x: x.score or 0, reverse=True)[:6]
    
    return spans, skills, coursework


def segment_jd_regex(jd_text: str) -> JDSpan:
    """Segment JD using regex patterns"""
    requirements: list[tuple[int, int]] = []
    responsibilities: list[tuple[int, int]] = []
    nice_to_haves: list[tuple[int, int]] = []
    
    # Patterns for requirements section
    req_patterns = [
        r"(?:requirements?|qualifications?|must have|required)[:\.]?\s*\n?(.*?)(?=\n\n|\n(?:responsibilities|preferred|nice to have|$))",
        r"(?:we are looking for|you must have|you should have)[:\.]?\s*\n?(.*?)(?=\n\n|\n(?:responsibilities|preferred|nice to have|$))",
    ]
    
    # Patterns for responsibilities section
    resp_patterns = [
        r"(?:responsibilities?|what you'll do|key responsibilities?)[:\.]?\s*\n?(.*?)(?=\n\n|\n(?:requirements?|preferred|nice to have|qualifications?|$))",
        r"(?:you will|you'll|duties)[:\.]?\s*\n?(.*?)(?=\n\n|\n(?:requirements?|preferred|nice to have|qualifications?|$))",
    ]
    
    # Patterns for nice-to-haves
    nth_patterns = [
        r"(?:nice to have|preferred|bonus|plus)[:\.]?\s*\n?(.*?)(?=\n\n|$)",
        r"(?:would be great|it's a plus|helpful if)[:\.]?\s*\n?(.*?)(?=\n\n|$)",
    ]
    
    for pattern in req_patterns:
        for match in re.finditer(pattern, jd_text, re.IGNORECASE | re.DOTALL):
            start, end = match.span(1)
            requirements.append((start, end))
    
    for pattern in resp_patterns:
        for match in re.finditer(pattern, jd_text, re.IGNORECASE | re.DOTALL):
            start, end = match.span(1)
            responsibilities.append((start, end))
    
    for pattern in nth_patterns:
        for match in re.finditer(pattern, jd_text, re.IGNORECASE | re.DOTALL):
            start, end = match.span(1)
            nice_to_haves.append((start, end))
    
    return JDSpan(
        requirements=requirements,
        responsibilities=responsibilities,
        nice_to_haves=nice_to_haves,
    )


async def segment_jd_llm(jd_text: str) -> JDSpan:
    """Segment JD using LLM (returns character index spans only)"""
    prompt = f"""Analyze this job description and return ONLY a JSON object with character index spans for three sections:
- "requirements": list of [start, end] tuples for required qualifications
- "responsibilities": list of [start, end] tuples for job responsibilities  
- "nice_to_haves": list of [start, end] tuples for preferred qualifications

Return ONLY the JSON, no explanation. The spans should be character indices in the original text.

Job Description:
{jd_text}

JSON:"""

    response = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a JSON-only API. Return only valid JSON with no markdown formatting."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
        max_tokens=500,
    )
    
    import json
    result_text = response.choices[0].message.content.strip()
    # Remove markdown code blocks if present
    result_text = re.sub(r"```json\n?", "", result_text)
    result_text = re.sub(r"```\n?", "", result_text)
    
    try:
        data = json.loads(result_text)
        return JDSpan(
            requirements=[tuple(span) for span in data.get("requirements", [])],
            responsibilities=[tuple(span) for span in data.get("responsibilities", [])],
            nice_to_haves=[tuple(span) for span in data.get("nice_to_haves", [])],
        )
    except (json.JSONDecodeError, KeyError, TypeError):
        # Fallback to regex if LLM fails
        return segment_jd_regex(jd_text)


def calculate_coverage(spans: JDSpan, total_length: int) -> float:
    """Calculate coverage percentage of JD text"""
    covered = set()
    for span_list in [spans.requirements, spans.responsibilities, spans.nice_to_haves]:
        for start, end in span_list:
            covered.update(range(start, end))
    return len(covered) / total_length if total_length > 0 else 0.0


def extract_skills_with_spacy(jd_text: str, spans: JDSpan) -> list[Skill]:
    """Extract skills using spaCy NER and phrase matching"""
    if nlp is None:
        return []
    
    skills_map: dict[str, Skill] = {}
    
    # Load skill taxonomy (simple version - can be enhanced with CSV)
    skill_taxonomy = load_skill_taxonomy()
    
    # Process each span section
    for span_list, source in [
        (spans.requirements, "requirement"),
        (spans.responsibilities, "responsibility"),
        (spans.nice_to_haves, "nice_to_have"),
    ]:
        for start, end in span_list:
            section_text = jd_text[start:end]
            doc = nlp(section_text)
            
            # Extract proper nouns and noun chunks
            for ent in doc.ents:
                if ent.label_ in ["ORG", "PRODUCT"]:
                    skill_name = ent.text.strip()
                    if skill_name in skill_taxonomy:
                        if skill_name not in skills_map:
                            skills_map[skill_name] = Skill(
                                name=skill_name,
                                source=source,
                                locked=False,
                                score=0,
                            )
                        else:
                            # Update source to highest priority
                            if source == "requirement" or skills_map[skill_name].source == "nice_to_have":
                                skills_map[skill_name].source = source
            
            # Match against taxonomy using phrase matching
            for pattern_text, skill_name in skill_taxonomy.items():
                if pattern_text.lower() in section_text.lower():
                    if skill_name not in skills_map:
                        skills_map[skill_name] = Skill(
                            name=skill_name,
                            source=source,
                            locked=False,
                            score=0,
                        )
    
    return list(skills_map.values())


def load_skill_taxonomy() -> dict[str, str]:
    """Load skill taxonomy with aliases"""
    # This is a simplified version - can be loaded from CSV
    taxonomy = {
        # Languages
        "python": "Python",
        "java": "Java",
        "javascript": "JavaScript",
        "typescript": "TypeScript",
        "c++": "C++",
        "c#": "C#",
        "go": "Go",
        "rust": "Rust",
        "ruby": "Ruby",
        "php": "PHP",
        "swift": "Swift",
        "kotlin": "Kotlin",
        # Frameworks
        "react": "React",
        "angular": "Angular",
        "vue": "Vue.js",
        "node.js": "Node.js",
        "express": "Express",
        "django": "Django",
        "flask": "Flask",
        "fastapi": "FastAPI",
        "spring": "Spring",
        "rails": "Ruby on Rails",
        # Databases
        "postgresql": "PostgreSQL",
        "mysql": "MySQL",
        "mongodb": "MongoDB",
        "redis": "Redis",
        "cassandra": "Cassandra",
        # Cloud
        "aws": "AWS",
        "azure": "Azure",
        "gcp": "Google Cloud",
        "docker": "Docker",
        "kubernetes": "Kubernetes",
        # ML/AI
        "tensorflow": "TensorFlow",
        "pytorch": "PyTorch",
        "scikit-learn": "scikit-learn",
        "machine learning": "Machine Learning",
        "deep learning": "Deep Learning",
    }
    
    # Create reverse mapping (normalized)
    reverse_map: dict[str, str] = {}
    for key, value in taxonomy.items():
        reverse_map[key.lower()] = value
        reverse_map[value.lower()] = value
    
    return reverse_map


def extract_coursework(jd_text: str) -> list[CourseworkItem]:
    """Extract coursework mentions from JD"""
    if nlp is None:
        return []
    
    coursework: list[CourseworkItem] = []
    doc = nlp(jd_text)
    
    # Look for course-related patterns
    course_patterns = [
        r"(?:course|class|coursework) in ([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
        r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:course|class)",
    ]
    
    for pattern in course_patterns:
        for match in re.finditer(pattern, jd_text, re.IGNORECASE):
            course_name = match.group(1).strip()
            if len(course_name) > 3:  # Filter out very short matches
                coursework.append(
                    CourseworkItem(
                        name=course_name,
                        score=1.0,  # Default score
                    )
                )
    
    return coursework


def score_and_sort_skills(
    skills: list[Skill],
    spans: JDSpan,
    jd_text: str,
) -> list[Skill]:
    """Score and sort skills by priority"""
    # Score mapping: requirement=3, responsibility=2, nice_to_have=1, static=0
    score_map = {
        "requirement": 3.0,
        "responsibility": 2.0,
        "nice_to_have": 1.0,
        "static": 0.0,
    }
    
    # Calculate scores
    for skill in skills:
        base_score = score_map.get(skill.source, 0.0)
        # Count occurrences in JD
        occurrences = jd_text.lower().count(skill.name.lower())
        skill.score = base_score + (occurrences * 0.1)
    
    # Stable sort by score (descending)
    skills.sort(key=lambda s: (s.score or 0.0, s.name), reverse=True)
    
    return skills

