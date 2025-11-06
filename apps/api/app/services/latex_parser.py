"""LaTeX parsing service for Master Resume"""

import re
from typing import Any

from app.services.types import ParsedResume, Skill, CourseworkItem


def parse_latex_resume(latex: str) -> ParsedResume:
    """
    Parse LaTeX resume into structured JSON.
    
    Extracts:
    - Sections by \section{} headers
    - Technical Skills from \textbf{} and comma lists
    - Relevant Coursework from list items
    """
    sections: dict[str, str] = {}
    technical_skills: list[Skill] = []
    relevant_coursework: list[CourseworkItem] = []

    # Extract sections by \section{} headers
    section_pattern = r"\\section\{([^}]+)\}(.*?)(?=\\section|$)"
    for match in re.finditer(section_pattern, latex, re.DOTALL):
        section_name = match.group(1).strip()
        section_content = match.group(2).strip()
        sections[section_name] = section_content

    # Extract Technical Skills
    # Look for patterns like \textbf{Technical Skills} followed by content
    skills_section_pattern = r"\\textbf\{[^}]*[Ss]kill[^}]*\}(.*?)(?=\\section|\\textbf|$)"
    skills_match = re.search(skills_section_pattern, latex, re.IGNORECASE | re.DOTALL)
    
    if skills_match:
        skills_content = skills_match.group(1)
        # Extract items separated by commas or list items
        # Look for \textbf{skill} or plain comma-separated lists
        skill_items = re.findall(r"\\textbf\{([^}]+)\}", skills_content)
        if not skill_items:
            # Try comma-separated list
            skill_items = [s.strip() for s in re.split(r"[,\n]", skills_content) if s.strip()]
        
        for skill_name in skill_items:
            skill_name = skill_name.strip()
            if skill_name and len(skill_name) > 1:
                technical_skills.append(
                    Skill(
                        name=skill_name,
                        source="static",
                        locked=False,  # Will be updated later based on projects
                        score=0,
                    )
                )

    # Extract Relevant Coursework
    # Look for patterns like \textbf{Relevant Coursework} or \section{Relevant Coursework}
    coursework_pattern = r"(?:\\textbf\{|\\section\{)[^}]*[Cc]oursework[^}]*\}(.*?)(?=\\section|\\textbf|$)"
    coursework_match = re.search(coursework_pattern, latex, re.IGNORECASE | re.DOTALL)
    
    if coursework_match:
        coursework_content = coursework_match.group(1)
        # Extract list items (common patterns)
        # \item or - or numbered lists
        coursework_items = re.findall(r"(?:\\item|[-•])\s*([^\n]+)", coursework_content)
        if not coursework_items:
            # Try line-by-line
            coursework_items = [line.strip() for line in coursework_content.split("\n") if line.strip() and not line.strip().startswith("\\")]
        
        for item_name in coursework_items:
            item_name = item_name.strip()
            if item_name and len(item_name) > 1:
                relevant_coursework.append(
                    CourseworkItem(
                        name=item_name,
                        score=0,
                    )
                )

    # Detect locked skills from projects section
    projects_section = sections.get("Projects", "") or sections.get("PROJECTS", "")
    if projects_section:
        # Extract technologies mentioned in project descriptions
        project_skills = extract_skills_from_projects(projects_section)
        for skill in technical_skills:
            if skill.name.lower() in [ps.lower() for ps in project_skills]:
                skill.locked = True

    return ParsedResume(
        sections=sections,
        technicalSkills=technical_skills,
        relevantCoursework=relevant_coursework,
    )


def extract_skills_from_projects(projects_content: str) -> list[str]:
    """Extract skill names mentioned in projects section"""
    # Look for common technology mentions
    # This is a simple heuristic - can be enhanced
    tech_keywords = [
        "Python", "Java", "JavaScript", "TypeScript", "React", "Node.js",
        "Docker", "Kubernetes", "AWS", "GCP", "Azure",
        "PostgreSQL", "MongoDB", "Redis", "MySQL",
        "TensorFlow", "PyTorch", "scikit-learn",
        "FastAPI", "Flask", "Django", "Express",
        "Git", "Linux", "CI/CD",
    ]
    
    found_skills = []
    content_lower = projects_content.lower()
    for keyword in tech_keywords:
        if keyword.lower() in content_lower:
            found_skills.append(keyword)
    
    return found_skills


def rebuild_latex_from_parsed(
    master_latex: str,
    parsed: ParsedResume,
    skills: list[Skill],
    coursework: list[CourseworkItem],
) -> str:
    """Rebuild LaTeX from parsed structure with updated skills and coursework"""
    result = master_latex

    # Update Technical Skills section
    skills_section_pattern = r"(\\textbf\{[^}]*[Ss]kill[^}]*\})(.*?)(?=\\section|\\textbf|$)"
    skills_match = re.search(skills_section_pattern, result, re.IGNORECASE | re.DOTALL)
    
    if skills_match:
        # Get only enabled skills
        enabled_skills = [s for s in skills if s.name]
        if enabled_skills:
            skills_text = ", ".join([f"\\textbf{{{s.name}}}" for s in enabled_skills])
            result = result[:skills_match.start(2)] + skills_text + result[skills_match.end(2):]

    # Update Relevant Coursework section
    coursework_pattern = r"(?:\\textbf\{|\\section\{)([^}]*[Cc]oursework[^}]*)\}(.*?)(?=\\section|\\textbf|$)"
    coursework_match = re.search(coursework_pattern, result, re.IGNORECASE | re.DOTALL)
    
    if coursework_match:
        # Get only enabled coursework (top 6)
        enabled_coursework = [c for c in coursework[:6] if c.name]
        if enabled_coursework:
            coursework_text = "\n".join([f"\\item {c.name}" for c in enabled_coursework])
            result = result[:coursework_match.start(2)] + coursework_text + result[coursework_match.end(2):]

    return result

