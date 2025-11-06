"""DM message generation service"""

from openai import AsyncOpenAI

from app.config import settings
from app.models import Job, OutreachContact

openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def generate_dm(
    contact: OutreachContact | None = None,
    job: Job | None = None,
    role: str | None = None,
    name: str | None = None,
) -> str:
    """Generate a LinkedIn DM message"""
    contact_name = name or (contact.name if contact else "there")
    contact_role = role or (contact.role if contact else None)
    
    context = []
    if job:
        context.append(f"Job: {job.title} at {job.company}")
        if job.jd_raw:
            context.append(f"Job Description: {job.jd_raw[:500]}")
    
    if contact_role:
        context.append(f"Contact's Role: {contact_role}")
    
    prompt = f"""Generate a brief, professional LinkedIn DM message for outreach.
Recipient: {contact_name}
{"Contact's Role: " + contact_role if contact_role else ""}
{"Context: " + " | ".join(context) if context else ""}

Keep it:
- Under 300 characters
- Professional but friendly
- Compliant with LinkedIn ToS
- Focused on connection, not sales

Return ONLY the message text, no greeting or signature."""

    response = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You generate brief, professional LinkedIn DM messages. Keep them under 300 characters and ToS-compliant.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=150,
    )
    
    return response.choices[0].message.content.strip()

