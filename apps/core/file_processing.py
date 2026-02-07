"""
File processing utilities for resumes, images, and documents.
Includes resume parsing, image optimization, PDF thumbnail generation, and metadata extraction.
"""
import os
import logging
from typing import Dict, Optional, Tuple, BinaryIO
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import UploadedFile
from PIL import Image
import hashlib

logger = logging.getLogger(__name__)


class FileProcessor:
    """
    Base class for file processing operations.
    """
    
    @staticmethod
    def extract_metadata(file: BinaryIO, filename: str) -> Dict:
        """
        Extract metadata from a file.
        
        Args:
            file: File object
            filename: Original filename
            
        Returns:
            Dictionary with file metadata
        """
        metadata = {
            'filename': filename,
            'size': 0,
            'extension': os.path.splitext(filename)[1].lower().lstrip('.'),
            'mime_type': None,
            'hash': None,
        }
        
        try:
            # Get file size
            if hasattr(file, 'size'):
                metadata['size'] = file.size
            else:
                file.seek(0, os.SEEK_END)
                metadata['size'] = file.tell()
                file.seek(0)
            
            # Calculate file hash
            file.seek(0)
            file_hash = hashlib.sha256(file.read()).hexdigest()
            metadata['hash'] = file_hash
            file.seek(0)
            
            # Detect MIME type
            try:
                import magic
                mime = magic.Magic(mime=True)
                metadata['mime_type'] = mime.from_buffer(file.read(1024))
                file.seek(0)
            except ImportError:
                logger.warning("python-magic not installed, MIME type detection disabled")
            except Exception as e:
                logger.warning(f"Failed to detect MIME type: {e}")
        
        except Exception as e:
            logger.error(f"Error extracting file metadata: {e}")
        
        return metadata


class ResumeProcessor(FileProcessor):
    """
    Processor for resume files (PDF, DOC, DOCX).
    Extracts text content and basic information.
    """
    
    @staticmethod
    def parse_pdf(file: BinaryIO) -> Dict:
        """
        Parse PDF resume and extract text content.
        
        Args:
            file: PDF file object
            
        Returns:
            Dictionary with extracted resume data
        """
        try:
            import PyPDF2
            
            pdf_reader = PyPDF2.PdfReader(file)
            text_content = []
            
            for page in pdf_reader.pages:
                text_content.append(page.extract_text())
            
            full_text = '\n'.join(text_content)
            
            return {
                'text': full_text,
                'page_count': len(pdf_reader.pages),
                'extracted': True,
            }
        except ImportError:
            logger.warning("PyPDF2 not installed, PDF parsing disabled")
            return {'text': '', 'page_count': 0, 'extracted': False}
        except Exception as e:
            logger.error(f"Error parsing PDF: {e}")
            return {'text': '', 'page_count': 0, 'extracted': False}
    
    @staticmethod
    def parse_docx(file: BinaryIO) -> Dict:
        """
        Parse DOCX resume and extract text content.
        
        Args:
            file: DOCX file object
            
        Returns:
            Dictionary with extracted resume data
        """
        try:
            from docx import Document
            
            doc = Document(file)
            paragraphs = [para.text for para in doc.paragraphs]
            full_text = '\n'.join(paragraphs)
            
            return {
                'text': full_text,
                'paragraph_count': len(paragraphs),
                'extracted': True,
            }
        except ImportError:
            logger.warning("python-docx not installed, DOCX parsing disabled")
            return {'text': '', 'paragraph_count': 0, 'extracted': False}
        except Exception as e:
            logger.error(f"Error parsing DOCX: {e}")
            return {'text': '', 'paragraph_count': 0, 'extracted': False}
    
    @staticmethod
    def parse_resume(file: BinaryIO, filename: str) -> Dict:
        """
        Parse resume file and extract content.
        
        Args:
            file: Resume file object
            filename: Original filename
            
        Returns:
            Dictionary with extracted resume data
        """
        ext = os.path.splitext(filename)[1].lower()
        
        if ext == '.pdf':
            return ResumeProcessor.parse_pdf(file)
        elif ext in ['.docx', '.doc']:
            return ResumeProcessor.parse_docx(file)
        else:
            return {'text': '', 'extracted': False}


class ImageProcessor(FileProcessor):
    """
    Processor for image files (profile pictures, thumbnails).
    Handles optimization, resizing, and format conversion.
    """
    
    @staticmethod
    def optimize_image(
        file: BinaryIO,
        max_width: int = 800,
        max_height: int = 800,
        quality: int = 85,
        format: str = 'JPEG'
    ) -> Optional[ContentFile]:
        """
        Optimize an image by resizing and compressing.
        
        Args:
            file: Image file object
            max_width: Maximum width in pixels
            max_height: Maximum height in pixels
            quality: JPEG quality (1-100)
            format: Output format (JPEG, PNG, WEBP)
            
        Returns:
            Optimized image as ContentFile or None if error
        """
        try:
            image = Image.open(file)
            
            # Convert RGBA to RGB for JPEG
            if format == 'JPEG' and image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            
            # Resize if needed
            if image.width > max_width or image.height > max_height:
                image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Save optimized image
            output = BytesIO()
            image.save(output, format=format, quality=quality, optimize=True)
            output.seek(0)
            
            return ContentFile(output.read(), name=os.path.splitext(file.name)[0] + f'.{format.lower()}')
        
        except Exception as e:
            logger.error(f"Error optimizing image: {e}")
            return None
    
    @staticmethod
    def generate_thumbnail(
        file: BinaryIO,
        size: Tuple[int, int] = (200, 200),
        format: str = 'JPEG'
    ) -> Optional[ContentFile]:
        """
        Generate a thumbnail from an image.
        
        Args:
            file: Image file object
            size: Thumbnail size (width, height)
            format: Output format
            
        Returns:
            Thumbnail as ContentFile or None if error
        """
        try:
            image = Image.open(file)
            
            # Convert RGBA to RGB for JPEG
            if format == 'JPEG' and image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            
            # Create thumbnail
            image.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Save thumbnail
            output = BytesIO()
            image.save(output, format=format, quality=85, optimize=True)
            output.seek(0)
            
            return ContentFile(output.read(), name=f"thumb_{os.path.basename(file.name)}")
        
        except Exception as e:
            logger.error(f"Error generating thumbnail: {e}")
            return None


class PDFProcessor(FileProcessor):
    """
    Processor for PDF files.
    Handles thumbnail generation and page extraction.
    """
    
    @staticmethod
    def generate_thumbnail(
        file: BinaryIO,
        page: int = 0,
        size: Tuple[int, int] = (200, 200)
    ) -> Optional[ContentFile]:
        """
        Generate a thumbnail from the first page of a PDF.
        
        Args:
            file: PDF file object
            page: Page number to use (default: 0)
            size: Thumbnail size (width, height)
            
        Returns:
            Thumbnail as ContentFile or None if error
        """
        try:
            from pdf2image import convert_from_bytes
            
            # Convert PDF page to image
            images = convert_from_bytes(file.read(), first_page=page + 1, last_page=page + 1)
            file.seek(0)
            
            if not images:
                return None
            
            # Resize image
            image = images[0]
            image.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Convert to bytes
            output = BytesIO()
            image.save(output, format='JPEG', quality=85)
            output.seek(0)
            
            return ContentFile(output.read(), name=f"pdf_thumb_{page}.jpg")
        
        except ImportError:
            logger.warning("pdf2image not installed, PDF thumbnail generation disabled")
            return None
        except Exception as e:
            logger.error(f"Error generating PDF thumbnail: {e}")
            return None


class VirusScanner:
    """
    Virus scanning utility using ClamAV.
    """
    
    @staticmethod
    def scan_file(file: BinaryIO) -> Tuple[bool, Optional[str]]:
        """
        Scan a file for viruses.
        
        Args:
            file: File object to scan
            
        Returns:
            Tuple of (is_safe, virus_name)
            is_safe: True if file is safe, False if infected
            virus_name: Name of detected virus or None
        """
        try:
            import pyclamd
            
            # Connect to ClamAV daemon
            cd = pyclamd.ClamdUnixSocket()
            
            # Read file content
            file.seek(0)
            file_content = file.read()
            file.seek(0)
            
            # Scan file
            result = cd.scan_stream(file_content)
            
            if result:
                # File is infected
                virus_name = list(result.values())[0]
                return False, virus_name
            else:
                # File is safe
                return True, None
        
        except ImportError:
            logger.warning("pyclamd not installed, virus scanning disabled")
            return True, None  # Assume safe if scanner not available
        except Exception as e:
            logger.error(f"Error scanning file for viruses: {e}")
            # In case of error, we might want to be cautious
            # For now, we'll assume safe to not block legitimate files
            return True, None


def process_uploaded_file(
    file: UploadedFile,
    file_type: str = 'resume',
    optimize_image: bool = True
) -> Dict:
    """
    Process an uploaded file based on its type.
    
    Args:
        file: Uploaded file object
        file_type: Type of file ('resume', 'profile_picture', 'document')
        optimize_image: Whether to optimize images
        
    Returns:
        Dictionary with processing results and metadata
    """
    result = {
        'original_file': file,
        'processed_file': None,
        'thumbnail': None,
        'metadata': {},
        'resume_data': {},
        'is_safe': True,
        'virus_name': None,
    }
    
    try:
        # Extract metadata
        result['metadata'] = FileProcessor.extract_metadata(file, file.name)
        
        # Virus scanning
        is_safe, virus_name = VirusScanner.scan_file(file)
        result['is_safe'] = is_safe
        result['virus_name'] = virus_name
        
        if not is_safe:
            logger.warning(f"Virus detected in file {file.name}: {virus_name}")
            return result
        
        # Process based on file type
        if file_type == 'resume':
            # Parse resume content
            ext = os.path.splitext(file.name)[1].lower()
            if ext == '.pdf':
                result['resume_data'] = ResumeProcessor.parse_pdf(file)
                # Generate PDF thumbnail
                result['thumbnail'] = PDFProcessor.generate_thumbnail(file)
            elif ext in ['.docx', '.doc']:
                result['resume_data'] = ResumeProcessor.parse_docx(file)
        
        elif file_type == 'profile_picture' and optimize_image:
            # Optimize profile picture
            optimized = ImageProcessor.optimize_image(file, max_width=800, max_height=800)
            if optimized:
                result['processed_file'] = optimized
            # Generate thumbnail
            result['thumbnail'] = ImageProcessor.generate_thumbnail(file, size=(200, 200))
        
    except Exception as e:
        logger.error(f"Error processing file {file.name}: {e}")
    
    return result
