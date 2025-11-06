"""PDF compilation task using Tectonic in Docker"""

import os
import tempfile
import structlog
from uuid import UUID
from pathlib import Path
import docker

from worker.config import settings

logger = structlog.get_logger()
docker_client = docker.from_env()


def compile_resume_task(variant_id: str):
    """
    Compile resume variant to PDF using Tectonic in Docker sandbox.
    
    Args:
        variant_id: UUID of the resume variant to compile
    """
    logger.info("Starting resume compilation", variant_id=variant_id)
    
    try:
        # Get variant from database (using sync connection for Celery)
        from sqlalchemy import create_engine, text
        from worker.config import settings
        
        # Create database engine
        engine = create_engine(
            settings.SUPABASE_URL.replace("https://", "postgresql://") + "/postgres",
            pool_pre_ping=True,
        )
        
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT latex_blob, pdf_path FROM resume_variant WHERE id = :id"),
                {"id": variant_id}
            )
            row = result.fetchone()
            
            if not row:
                logger.error("Variant not found", variant_id=variant_id)
                return {"status": "error", "message": "Variant not found"}
            
            latex_blob = row[0]
        
        # Create temporary directory for LaTeX file
        with tempfile.TemporaryDirectory() as tmpdir:
            latex_file = Path(tmpdir) / "resume.tex"
            latex_file.write_text(latex_blob)
            
            # Create output directory
            output_dir = Path(tmpdir) / "output"
            output_dir.mkdir()
            
            # Run Tectonic in Docker container (sandboxed, no network)
            logger.info("Running Tectonic compilation", variant_id=variant_id)
            
            container = docker_client.containers.run(
                image="ghcr.io/tectonic-typesetting/tectonic:latest",
                command=[
                    "tectonic",
                    "--outdir", "/output",
                    "/input/resume.tex",
                ],
                volumes={
                    str(latex_file.parent): {"bind": "/input", "mode": "ro"},
                    str(output_dir): {"bind": "/output", "mode": "rw"},
                },
                network_disabled=True,  # Sandbox: no network access
                remove=True,
                detach=False,
            )
            
            # Check for PDF output
            pdf_file = output_dir / "resume.pdf"
            if not pdf_file.exists():
                logger.error("PDF compilation failed", variant_id=variant_id)
                return {"status": "error", "message": "PDF compilation failed"}
            
            # Upload PDF to Supabase Storage
            from supabase import create_client, Client
            supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            
            pdf_path = f"resumes/{variant_id}/resume.pdf"
            with open(pdf_file, "rb") as f:
                pdf_data = f.read()
            
            supabase.storage.from_("resumes").upload(
                pdf_path,
                pdf_data,
                file_options={"content-type": "application/pdf"},
                upsert=True,
            )
            
            # Store just the path (not URL - will generate signed URL in API)
            # Update variant with PDF path
            with engine.connect() as conn:
                conn.execute(
                    text("UPDATE resume_variant SET pdf_path = :path WHERE id = :id"),
                    {"path": pdf_path, "id": variant_id}
                )
                conn.commit()
            
            logger.info("Resume compilation completed", variant_id=variant_id, pdf_path=pdf_path)
            
            return {
                "status": "success",
                "variant_id": variant_id,
                "pdf_path": pdf_path,
            }
    
    except Exception as e:
        logger.error("Compilation error", variant_id=variant_id, exc_info=e)
        return {"status": "error", "message": str(e)}

