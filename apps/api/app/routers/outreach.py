"""Outreach management routes"""

from uuid import UUID
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.database import get_db
from app.models import OutreachContact, Job, Action
from app.middleware.auth import get_current_user_id
from app.services.dm_generator import generate_dm

router = APIRouter()


class CreateContactRequest(BaseModel):
    """Request model for creating a contact"""
    job_id: Optional[UUID] = None
    name: str
    linkedin_url: Optional[str] = None
    role: Optional[str] = None
    notes: Optional[str] = None


class UpdateContactRequest(BaseModel):
    """Request model for updating a contact"""
    name: Optional[str] = None
    linkedin_url: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class GenerateDMRequest(BaseModel):
    """Request model for generating DM"""
    contact_id: Optional[UUID] = None
    job_id: Optional[UUID] = None
    role: Optional[str] = None
    name: Optional[str] = None


@router.post("/contacts")
async def create_contact(
    request: CreateContactRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Create a new outreach contact"""
    # Verify job if provided
    if request.job_id:
        job_result = await db.execute(
            select(Job).where(Job.id == request.job_id, Job.user_id == user_id)
        )
        job = job_result.scalar_one_or_none()
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found",
            )
    
    new_contact = OutreachContact(
        user_id=user_id,
        job_id=request.job_id,
        name=request.name,
        linkedin_url=request.linkedin_url,
        role=request.role,
        notes=request.notes,
    )
    db.add(new_contact)
    await db.commit()
    await db.refresh(new_contact)
    
    return {
        "id": str(new_contact.id),
        "name": new_contact.name,
        "status": new_contact.status,
        "created_at": new_contact.created_at.isoformat(),
    }


@router.get("/contacts")
async def list_contacts(
    job_id: Optional[UUID] = None,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """List all outreach contacts"""
    query = select(OutreachContact).where(OutreachContact.user_id == user_id)
    
    if job_id:
        query = query.where(OutreachContact.job_id == job_id)
    
    result = await db.execute(query)
    contacts = result.scalars().all()
    
    return [
        {
            "id": str(contact.id),
            "job_id": str(contact.job_id) if contact.job_id else None,
            "name": contact.name,
            "linkedin_url": contact.linkedin_url,
            "role": contact.role,
            "status": contact.status,
            "last_contacted_at": contact.last_contacted_at.isoformat() if contact.last_contacted_at else None,
            "notes": contact.notes,
            "created_at": contact.created_at.isoformat(),
        }
        for contact in contacts
    ]


@router.get("/contacts/{contact_id}")
async def get_contact(
    contact_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific contact"""
    result = await db.execute(
        select(OutreachContact).where(
            OutreachContact.id == contact_id,
            OutreachContact.user_id == user_id,
        )
    )
    contact = result.scalar_one_or_none()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )
    
    return {
        "id": str(contact.id),
        "job_id": str(contact.job_id) if contact.job_id else None,
        "name": contact.name,
        "linkedin_url": contact.linkedin_url,
        "role": contact.role,
        "status": contact.status,
        "last_contacted_at": contact.last_contacted_at.isoformat() if contact.last_contacted_at else None,
        "notes": contact.notes,
        "created_at": contact.created_at.isoformat(),
    }


@router.patch("/contacts/{contact_id}")
async def update_contact(
    contact_id: UUID,
    request: UpdateContactRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Update a contact"""
    result = await db.execute(
        select(OutreachContact).where(
            OutreachContact.id == contact_id,
            OutreachContact.user_id == user_id,
        )
    )
    contact = result.scalar_one_or_none()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )
    
    # Update fields
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contact, field, value)
    
    await db.commit()
    await db.refresh(contact)
    
    return {
        "id": str(contact.id),
        "name": contact.name,
        "status": contact.status,
        "message": "Contact updated",
    }


@router.post("/generate-dm")
async def generate_dm_endpoint(
    request: GenerateDMRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Generate a DM message for outreach"""
    job = None
    contact = None
    
    # Get job if provided
    if request.job_id:
        job_result = await db.execute(
            select(Job).where(Job.id == request.job_id, Job.user_id == user_id)
        )
        job = job_result.scalar_one_or_none()
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found",
            )
    
    # Get contact if provided
    if request.contact_id:
        contact_result = await db.execute(
            select(OutreachContact).where(
                OutreachContact.id == request.contact_id,
                OutreachContact.user_id == user_id,
            )
        )
        contact = contact_result.scalar_one_or_none()
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found",
            )
    
    # Generate DM
    dm_text = await generate_dm(
        contact=contact,
        job=job,
        role=request.role,
        name=request.name,
    )
    
    # Log action
    action = Action(
        user_id=user_id,
        job_id=request.job_id,
        type="outreach_dm_generated",
        meta={"contact_id": str(request.contact_id) if request.contact_id else None},
    )
    db.add(action)
    await db.commit()
    
    return {
        "dm_text": dm_text,
        "message": "DM generated",
    }

