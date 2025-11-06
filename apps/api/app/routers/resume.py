"""Resume management routes"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.database import get_db
from app.models import ResumeMaster, ResumeVariant, Job
from app.middleware.auth import get_current_user_id
from app.services.latex_parser import parse_latex_resume, rebuild_latex_from_parsed
from app.services.types import Skill, CourseworkItem
from app.services.storage import get_signed_url

router = APIRouter()


class UploadResumeRequest(BaseModel):
    """Request model for uploading master resume"""
    latex: str


class UpdateResumeVariantRequest(BaseModel):
    """Request model for updating resume variant"""
    job_id: UUID
    skills: list[Skill]
    coursework: list[CourseworkItem]


@router.post("/master")
async def upload_master_resume(
    request: UploadResumeRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Upload or update master resume"""
    # Parse LaTeX
    parsed = parse_latex_resume(request.latex)
    
    # Check if master resume exists
    result = await db.execute(
        select(ResumeMaster).where(ResumeMaster.user_id == user_id)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        # Update existing
        existing.latex_blob = request.latex
        existing.parsed_json = parsed.model_dump()
        await db.commit()
        await db.refresh(existing)
        return {
            "id": str(existing.id),
            "parsed": parsed.model_dump(),
            "message": "Master resume updated",
        }
    else:
        # Create new
        new_master = ResumeMaster(
            user_id=user_id,
            latex_blob=request.latex,
            parsed_json=parsed.model_dump(),
        )
        db.add(new_master)
        await db.commit()
        await db.refresh(new_master)
        return {
            "id": str(new_master.id),
            "parsed": parsed.model_dump(),
            "message": "Master resume created",
        }


@router.get("/master")
async def get_master_resume(
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get master resume"""
    result = await db.execute(
        select(ResumeMaster).where(ResumeMaster.user_id == user_id)
    )
    master = result.scalar_one_or_none()
    
    if not master:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Master resume not found",
        )
    
    return {
        "id": str(master.id),
        "latex": master.latex_blob,
        "parsed": master.parsed_json,
    }


@router.post("/variant")
async def update_resume_variant(
    request: UpdateResumeVariantRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Update resume variant for a job"""
    # Get master resume
    master_result = await db.execute(
        select(ResumeMaster).where(ResumeMaster.user_id == user_id)
    )
    master = master_result.scalar_one_or_none()
    
    if not master:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Master resume not found. Please upload a master resume first.",
        )
    
    # Verify job exists
    job_result = await db.execute(
        select(Job).where(Job.id == request.job_id, Job.user_id == user_id)
    )
    job = job_result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    
    # Rebuild LaTeX
    from app.services.types import ParsedResume
    parsed = ParsedResume.model_validate(master.parsed_json)
    new_latex = rebuild_latex_from_parsed(
        master.latex_blob,
        parsed,
        request.skills,
        request.coursework,
    )
    
    # Get or create variant
    variant_result = await db.execute(
        select(ResumeVariant).where(
            ResumeVariant.user_id == user_id,
            ResumeVariant.job_id == request.job_id,
        )
    )
    variant = variant_result.scalar_one_or_none()
    
    if variant:
        variant.latex_blob = new_latex
        variant.diff_json = {
            "skills": [s.model_dump() for s in request.skills],
            "coursework": [c.model_dump() for c in request.coursework],
        }
        await db.commit()
        await db.refresh(variant)
    else:
        variant = ResumeVariant(
            user_id=user_id,
            job_id=request.job_id,
            latex_blob=new_latex,
            diff_json={
                "skills": [s.model_dump() for s in request.skills],
                "coursework": [c.model_dump() for c in request.coursework],
            },
        )
        db.add(variant)
        await db.commit()
        await db.refresh(variant)
    
    # Trigger PDF compilation (async via Celery)
    from app.tasks.compile import compile_resume_task
    compile_resume_task.delay(str(variant.id))
    
    return {
        "id": str(variant.id),
        "latex": variant.latex_blob,
        "message": "Resume variant updated. PDF compilation in progress.",
    }


@router.get("/variant/{job_id}")
async def get_resume_variant(
    job_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get resume variant for a job"""
    result = await db.execute(
        select(ResumeVariant).where(
            ResumeVariant.user_id == user_id,
            ResumeVariant.job_id == job_id,
        )
    )
    variant = result.scalar_one_or_none()
    
    if not variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume variant not found",
        )
    
    # Generate signed URL if PDF exists
    pdf_url = ""
    if variant.pdf_path:
        pdf_url = get_signed_url(variant.pdf_path)
    
    return {
        "id": str(variant.id),
        "latex": variant.latex_blob,
        "pdf_path": pdf_url,  # Return signed URL instead of path
        "diff": variant.diff_json,
    }

