"""Job management routes"""

from uuid import UUID
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from pydantic import BaseModel

from app.database import get_db
from app.models import Job, Action
from app.middleware.auth import get_current_user_id
from app.services.jd_analyzer import analyze_jd

router = APIRouter()


class CreateJobRequest(BaseModel):
    """Request model for creating a job"""
    title: str
    company: str
    location: Optional[str] = None
    jd_raw: str
    source_url: Optional[str] = None
    deadline_at: Optional[datetime] = None
    notes: Optional[str] = None


class UpdateJobRequest(BaseModel):
    """Request model for updating a job"""
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None
    application_status: Optional[str] = None
    connection_status: Optional[str] = None
    source_url: Optional[str] = None
    deadline_at: Optional[datetime] = None
    notes: Optional[str] = None


class AnalyzeJDRequest(BaseModel):
    """Request model for analyzing JD"""
    jd_text: str
    job_id: Optional[UUID] = None


@router.post("")
async def create_job(
    request: CreateJobRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Create a new job"""
    new_job = Job(
        user_id=user_id,
        title=request.title,
        company=request.company,
        location=request.location,
        jd_raw=request.jd_raw,
        source_url=request.source_url,
        deadline_at=request.deadline_at,
        notes=request.notes,
    )
    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)
    
    # Log action
    action = Action(
        user_id=user_id,
        job_id=new_job.id,
        type="job_added",
        meta={"title": request.title, "company": request.company},
    )
    db.add(action)
    await db.commit()
    
    return {
        "id": str(new_job.id),
        "title": new_job.title,
        "company": new_job.company,
        "status": new_job.status,
        "created_at": new_job.created_at.isoformat(),
    }


@router.get("")
async def list_jobs(
    status_filter: Optional[str] = Query(None, alias="status"),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """List all jobs for the user"""
    import structlog
    logger = structlog.get_logger()
    
    try:
        logger.info("Listing jobs", user_id=str(user_id), status_filter=status_filter)
        query = select(Job).where(Job.user_id == user_id)
        
        if status_filter:
            query = query.where(Job.status == status_filter)
        
        result = await db.execute(query)
        jobs = result.scalars().all()
        
        logger.info("Jobs retrieved", count=len(jobs))
        
        return [
            {
                "id": str(job.id),
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "status": job.status,
                "application_status": job.application_status,
                "connection_status": job.connection_status,
                "deadline_at": job.deadline_at.isoformat() if job.deadline_at else None,
                "created_at": job.created_at.isoformat(),
            }
            for job in jobs
        ]
    except Exception as e:
        logger.error("Error listing jobs", error=str(e), error_type=type(e).__name__)
        raise


@router.get("/{job_id}")
async def get_job(
    job_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific job"""
    result = await db.execute(
        select(Job).where(Job.id == job_id, Job.user_id == user_id)
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    
    return {
        "id": str(job.id),
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "jd_raw": job.jd_raw,
        "jd_spans_json": job.jd_spans_json,
        "status": job.status,
        "application_status": job.application_status,
        "connection_status": job.connection_status,
        "source_url": job.source_url,
        "deadline_at": job.deadline_at.isoformat() if job.deadline_at else None,
        "notes": job.notes,
        "created_at": job.created_at.isoformat(),
        "updated_at": job.updated_at.isoformat(),
    }


@router.patch("/{job_id}")
async def update_job(
    job_id: UUID,
    request: UpdateJobRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Update a job"""
    result = await db.execute(
        select(Job).where(Job.id == job_id, Job.user_id == user_id)
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    
    # Update fields
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job, field, value)
    
    await db.commit()
    await db.refresh(job)
    
    return {
        "id": str(job.id),
        "title": job.title,
        "company": job.company,
        "status": job.status,
        "message": "Job updated",
    }


@router.delete("/{job_id}")
async def delete_job(
    job_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Delete a job"""
    result = await db.execute(
        select(Job).where(Job.id == job_id, Job.user_id == user_id)
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    
    await db.delete(job)
    await db.commit()
    
    return {"message": "Job deleted"}


@router.post("/analyze-jd")
async def analyze_job_description(
    request: AnalyzeJDRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Analyze job description and extract skills"""
    # Analyze JD
    spans, skills, coursework = await analyze_jd(request.jd_text)
    
    # If job_id provided, update job with spans
    if request.job_id:
        job_result = await db.execute(
            select(Job).where(Job.id == request.job_id, Job.user_id == user_id)
        )
        job = job_result.scalar_one_or_none()
        
        if job:
            job.jd_spans_json = spans.model_dump()
            await db.commit()
    
    # Log action
    action = Action(
        user_id=user_id,
        job_id=request.job_id,
        type="jd_processed",
        meta={"jd_length": len(request.jd_text)},
    )
    db.add(action)
    await db.commit()
    
    return {
        "spans": spans.model_dump(),
        "skills": [s.model_dump() for s in skills],
        "coursework": [c.model_dump() for c in coursework],
    }

