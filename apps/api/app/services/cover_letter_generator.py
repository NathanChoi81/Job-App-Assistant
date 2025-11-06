"""Cover letter generation service"""

from openai import AsyncOpenAI

from app.config import settings
from app.models import Job

openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

# Cover letter template
COVER_LETTER_TEMPLATE = """{Company}

Dear Hiring Manager,

I am writing to express my interest in the {Role} position at {Company}. {MissionWhyMe}

{SkillFromInternship}

{CallToAction}

Sincerely,
[Your Name]"""


async def generate_cover_letter(job: Job) -> str:
    """Generate cover letter text from job description"""
    # Extract key information from JD
    prompt = f"""Generate a cover letter for the following job. Fill in the placeholders with specific, minimal edits.
Keep the template structure intact. Replace:
- {{Company}} with: {job.company}
- {{Role}} with: {job.title}
- {{MissionWhyMe}} with: 1-2 sentences about why you're interested and why you're a good fit
- {{SkillFromInternship}} with: 1-2 sentences highlighting a relevant skill or experience from your background
- {{CallToAction}} with: 1 sentence expressing enthusiasm and next steps

Job Description:
{job.jd_raw[:2000]}  # Limit to avoid token limits

Return ONLY the filled template, no additional text."""

    response = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a cover letter generator. Fill in placeholders with minimal, specific edits. Maintain the template structure.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=500,
    )
    
    return response.choices[0].message.content.strip()

