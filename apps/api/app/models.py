"""SQLAlchemy models"""

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import JSON, Text, TIMESTAMP, ForeignKey, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    """User model"""

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    email: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default="now()"
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default="now()", onupdate="now()"
    )


class ResumeMaster(Base):
    """Master Resume model"""

    __tablename__ = "resume_master"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    latex_blob: Mapped[str] = mapped_column(Text, nullable=False)
    parsed_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default="now()"
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default="now()", onupdate="now()"
    )

    __table_args__ = (
        Index("idx_resume_master_user_id", "user_id"),
    )


class Job(Base):
    """Job model"""

    __tablename__ = "jobs"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    company: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str | None] = mapped_column(Text, nullable=True)
    jd_raw: Mapped[str] = mapped_column(Text, nullable=False)
    jd_spans_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="Not Applied",
        server_default="Not Applied",
    )
    application_status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="Not Sent",
        server_default="Not Sent",
    )
    connection_status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="No Connection",
        server_default="No Connection",
    )
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    deadline_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default="now()"
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default="now()", onupdate="now()"
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('Not Applied', 'Applied', 'Interview', 'Offer', 'Rejected')",
            name="check_job_status",
        ),
        CheckConstraint(
            "application_status IN ('Not Sent', 'Sent', 'Waiting')",
            name="check_application_status",
        ),
        CheckConstraint(
            "connection_status IN ('No Connection', 'Reached Out', 'Connected')",
            name="check_connection_status",
        ),
        Index("idx_jobs_user_id", "user_id"),
        Index("idx_jobs_status", "status"),
    )


class ResumeVariant(Base):
    """Resume Variant model"""

    __tablename__ = "resume_variant"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    job_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False
    )
    latex_blob: Mapped[str] = mapped_column(Text, nullable=False)
    pdf_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    diff_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default="now()"
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default="now()", onupdate="now()"
    )

    __table_args__ = (
        Index("idx_resume_variant_user_job", "user_id", "job_id", unique=True),
    )


class CoverLetter(Base):
    """Cover Letter model"""

    __tablename__ = "cover_letters"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    job_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    pdf_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default="now()"
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default="now()", onupdate="now()"
    )

    __table_args__ = (
        Index("idx_cover_letters_job_id", "job_id"),
    )


class OutreachContact(Base):
    """Outreach Contact model"""

    __tablename__ = "outreach_contacts"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    job_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True
    )
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    linkedin_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    role: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="Not Contacted",
        server_default="Not Contacted",
    )
    last_contacted_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default="now()"
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default="now()", onupdate="now()"
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('Not Contacted', 'Reached Out', 'Connected', 'Not Interested')",
            name="check_contact_status",
        ),
        Index("idx_outreach_contacts_user_id", "user_id"),
        Index("idx_outreach_contacts_job_id", "job_id"),
    )


class Action(Base):
    """Action/Event model for analytics"""

    __tablename__ = "actions"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    job_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True
    )
    type: Mapped[str] = mapped_column(Text, nullable=False)
    meta: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default="now()"
    )

    __table_args__ = (
        CheckConstraint(
            "type IN ('jd_processed', 'resume_compiled', 'cover_letter_generated', 'job_added', 'outreach_dm_generated', 'resume_viewed', 'applied', 'connected', 'messaged')",
            name="check_action_type",
        ),
        Index("idx_actions_user_id", "user_id"),
        Index("idx_actions_type", "type"),
        Index("idx_actions_created_at", "created_at"),
    )

