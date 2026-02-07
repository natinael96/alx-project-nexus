"""
File processing tasks (synchronous).
"""
import logging
from apps.core.file_processing import ImageProcessor, PDFProcessor, VirusScanner, ResumeProcessor
from apps.core.storage import storage_manager
from django.conf import settings
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

logger = logging.getLogger(__name__)


def process_uploaded_file(file_path, file_type, user_id=None, job_id=None, application_id=None):
    """
    Process an uploaded file (e.g., image optimization, virus scanning, resume parsing).
    """
    logger.info(f"Starting file processing for {file_path} (type: {file_type})")
    try:
        # Retrieve the file from storage
        if not storage_manager.exists(file_path):
            logger.error(f"File not found in storage: {file_path}")
            return

        with storage_manager.storage.open(file_path, 'rb') as f:
            file_content = f.read()

        original_file_name = file_path.split('/')[-1]
        file_extension = original_file_name.split('.')[-1].lower()

        # Create an InMemoryUploadedFile for processing
        in_memory_file = InMemoryUploadedFile(
            BytesIO(file_content),
            None,
            original_file_name,
            file_type,
            len(file_content),
            None
        )

        # --- Image Optimization (for profile pictures) ---
        if file_type.startswith('image/') and getattr(settings, 'ENABLE_IMAGE_OPTIMIZATION', True):
            logger.info(f"Optimizing image: {file_path}")
            max_width = getattr(settings, 'MAX_IMAGE_WIDTH', 1920)
            max_height = getattr(settings, 'MAX_IMAGE_HEIGHT', 1080)
            quality = getattr(settings, 'IMAGE_QUALITY', 85)
            optimized_image = ImageProcessor.optimize_image(
                in_memory_file,
                max_width=max_width,
                max_height=max_height,
                quality=quality
            )
            if optimized_image:
                storage_manager.save(file_path, optimized_image)
                logger.info(f"Image optimized and saved: {file_path}")
            else:
                logger.warning(f"Image optimization failed for {file_path}")

        # --- PDF Thumbnail Generation (for resumes) ---
        if file_type == 'application/pdf' and application_id:
            logger.info(f"Generating PDF thumbnail for: {file_path}")
            thumbnail = PDFProcessor.generate_thumbnail(in_memory_file)
            if thumbnail:
                thumbnail_path = file_path.replace(f'.{file_extension}', '_thumbnail.jpg')
                storage_manager.save(thumbnail_path, thumbnail)
                logger.info(f"PDF thumbnail generated and saved: {thumbnail_path}")
            else:
                logger.warning(f"PDF thumbnail generation failed for {file_path}")

        # --- Virus Scanning ---
        if getattr(settings, 'ENABLE_VIRUS_SCANNING', False):
            logger.info(f"Scanning file for viruses: {file_path}")
            is_safe, virus_name = VirusScanner.scan_file(in_memory_file)
            if not is_safe:
                logger.warning(f"File {file_path} is infected with a virus: {virus_name}. Deleting file.")
                storage_manager.delete(file_path)
                return
            else:
                logger.info(f"File {file_path} is clean.")

        # --- Resume Parsing (for applications) ---
        if file_type in ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'] and application_id and getattr(settings, 'ENABLE_RESUME_PARSING', False):
            logger.info(f"Parsing resume: {file_path}")
            extracted_data = ResumeProcessor.parse_resume(in_memory_file, original_file_name)
            if extracted_data and extracted_data.get('extracted'):
                logger.info(f"Resume parsed for {file_path}. Extracted data: {list(extracted_data.keys())}")
            else:
                logger.warning(f"Resume parsing failed for {file_path}")

    except Exception as e:
        logger.error(f"Unhandled error during file processing for {file_path}: {e}", exc_info=True)
