"""Cover letter generation routes"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.database import get_db
from app.models import CoverLetter, Job, Action
from app.middleware.auth import get_current_user_id
from app.services.cover_letter_generator import generate_cover_letter
from app.services.storage import get_signed_url

router = APIRouter()


class GenerateCoverLetterRequest(BaseModel):
    """Request model for generating cover letter"""
    job_id: UUID


class UpdateCoverLetterRequest(BaseModel):
    """Request model for updating cover letter"""
    text: str


@router.post("/generate")
async def generate_cover_letter_endpoint(
    request: GenerateCoverLetterRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Generate a cover letter for a job"""
    # Get job
    job_result = await db.execute(
        select(Job).where(Job.id == request.job_id, Job.user_id == user_id)
    )
    job = job_result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    
    # Generate cover letter
    cover_letter_text = await generate_cover_letter(job)
    
    # Get or create cover letter
    cl_result = await db.execute(
        select(CoverLetter).where(CoverLetter.job_id == request.job_id)
    )
    cover_letter = cl_result.scalar_one_or_none()
    
    if cover_letter:
        cover_letter.text = cover_letter_text
        await db.commit()
        await db.refresh(cover_letter)
    else:
        cover_letter = CoverLetter(
            job_id=request.job_id,
            text=cover_letter_text,
        )
        db.add(cover_letter)
        await db.commit()
        await db.refresh(cover_letter)
    
    # Log action
    action = Action(
        user_id=user_id,
        job_id=request.job_id,
        type="cover_letter_generated",
        meta={},
    )
    db.add(action)
    await db.commit()
    
    return {
        "id": str(cover_letter.id),
        "text": cover_letter.text,
        "message": "Cover letter generated",
    }


@router.get("/{job_id}")
async def get_cover_letter(
    job_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get cover letter for a job"""
    # Verify job belongs to user
    job_result = await db.execute(
        select(Job).where(Job.id == job_id, Job.user_id == user_id)
    )
    job = job_result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    
    # Get cover letter
    cl_result = await db.execute(
        select(CoverLetter).where(CoverLetter.job_id == job_id)
    )
    cover_letter = cl_result.scalar_one_or_none()
    
    if not cover_letter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cover letter not found",
        )
    
    # Generate signed URL if PDF exists
    pdf_url = ""
    if cover_letter.pdf_path:
        pdf_url = get_signed_url(cover_letter.pdf_path)
    
    return {
        "id": str(cover_letter.id),
        "text": cover_letter.text,
        "pdf_path": pdf_url,  # Return signed URL instead of path
    }


@router.patch("/{job_id}")
async def update_cover_letter(
    job_id: UUID,
    request: UpdateCoverLetterRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Update cover letter text"""
    # Verify job belongs to user
    job_result = await db.execute(
        select(Job).where(Job.id == job_id, Job.user_id == user_id)
    )
    job = job_result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    
    # Get cover letter
    cl_result = await db.execute(
        select(CoverLetter).where(CoverLetter.job_id == job_id)
    )
    cover_letter = cl_result.scalar_one_or_none()
    
    if not cover_letter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cover letter not found",
        )
    
    cover_letter.text = request.text
    await db.commit()
    await db.refresh(cover_letter)
    
    return {
        "id": str(cover_letter.id),
        "text": cover_letter.text,
        "message": "Cover letter updated",
    }

