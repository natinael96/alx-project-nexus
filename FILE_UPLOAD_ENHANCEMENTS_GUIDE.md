# File Upload Enhancements - Implementation Guide

## ✅ File Upload Enhancements - Fully Implemented

### Overview

A comprehensive file upload enhancement system has been implemented for the Job Board Platform, including cloud storage integration (Supabase), file processing, virus scanning, secure downloads, and automated cleanup.

---

## 🗄️ File Storage System

### ✅ Storage Abstraction Layer

**Location**: `apps/core/storage.py`

**Features:**
- **Unified Interface**: Single API for multiple storage backends
- **Multiple Backends**: Support for Local and Supabase Storage
- **Automatic Fallback**: Falls back to local storage if cloud storage fails
- **Signed URLs**: Secure, time-limited file access

**Storage Backends:**

1. **LocalStorageBackend** (Default)
   - Uses Django's default file storage
   - Suitable for development and small deployments
   - No additional configuration required

2. **SupabaseStorageBackend**
   - Cloud storage via Supabase Storage
   - Automatic bucket management
   - Public and signed URL support
   - Configuration via environment variables

### ✅ Storage Manager

**Singleton Pattern**: Global `storage_manager` instance provides unified access

**Methods:**
- `save(name, content)` - Save file
- `delete(name)` - Delete file
- `exists(name)` - Check if file exists
- `url(name)` - Get public URL
- `size(name)` - Get file size
- `generate_signed_url(name, expiration)` - Generate secure URL

---

## 🔧 File Processing

### ✅ Resume Processing

**Location**: `apps/core/file_processing.py` - `ResumeProcessor`

**Features:**
- **PDF Parsing**: Extract text from PDF resumes using PyPDF2
- **DOCX Parsing**: Extract text from Word documents using python-docx
- **Content Extraction**: Full text extraction for search/indexing
- **Metadata Extraction**: Page count, paragraph count, etc.

**Usage:**
```python
from apps.core.file_processing import ResumeProcessor

resume_data = ResumeProcessor.parse_resume(file, filename)
# Returns: {'text': '...', 'page_count': 2, 'extracted': True}
```

### ✅ Image Processing

**Location**: `apps/core/file_processing.py` - `ImageProcessor`

**Features:**
- **Image Optimization**: Resize and compress images
- **Format Conversion**: Convert to JPEG/PNG/WEBP
- **Thumbnail Generation**: Create thumbnails for profile pictures
- **Quality Control**: Configurable quality settings

**Configuration:**
- `MAX_IMAGE_WIDTH`: 800px (default)
- `MAX_IMAGE_HEIGHT`: 800px (default)
- `IMAGE_QUALITY`: 85% (default)

**Usage:**
```python
from apps.core.file_processing import ImageProcessor

optimized = ImageProcessor.optimize_image(file, max_width=800, max_height=800)
thumbnail = ImageProcessor.generate_thumbnail(file, size=(200, 200))
```

### ✅ PDF Processing

**Location**: `apps/core/file_processing.py` - `PDFProcessor`

**Features:**
- **Thumbnail Generation**: Create thumbnails from PDF first page
- **Page Extraction**: Extract specific pages
- **Image Conversion**: Convert PDF pages to images

**Usage:**
```python
from apps.core.file_processing import PDFProcessor

thumbnail = PDFProcessor.generate_thumbnail(file, page=0, size=(200, 200))
```

### ✅ Virus Scanning

**Location**: `apps/core/file_processing.py` - `VirusScanner`

**Features:**
- **ClamAV Integration**: Virus scanning via ClamAV daemon
- **Stream Scanning**: Scan files in memory
- **Safe Fallback**: Assumes safe if scanner unavailable

**Configuration:**
- `ENABLE_VIRUS_SCANNING`: Enable/disable scanning (default: False)

**Usage:**
```python
from apps.core.file_processing import VirusScanner

is_safe, virus_name = VirusScanner.scan_file(file)
if not is_safe:
    # Handle infected file
    pass
```

### ✅ File Metadata Extraction

**Location**: `apps/core/file_processing.py` - `FileProcessor`

**Features:**
- **File Size**: Automatic size detection
- **MIME Type**: Content type detection (via python-magic)
- **File Hash**: SHA256 hash for deduplication
- **Extension Detection**: Automatic extension parsing

**Usage:**
```python
from apps.core.file_processing import FileProcessor

metadata = FileProcessor.extract_metadata(file, filename)
# Returns: {'filename': '...', 'size': 12345, 'mime_type': '...', 'hash': '...'}
```

---

## 🔒 File Access Control

### ✅ Access Control System

**Location**: `apps/core/file_management.py` - `FileAccessControl`

**Resume Access Rules:**
- **Admin**: Can access all resumes
- **Applicant**: Can access their own resumes
- **Employer**: Can access resumes for their jobs
- **Others**: No access

**Profile Picture Access Rules:**
- **Owner**: Can always access their own picture
- **Public**: Profile pictures are generally public (configurable)

### ✅ Secure Download URLs

**Location**: `apps/core/views_file_download.py`

**Endpoints:**
- `GET /api/files/resumes/<application_id>/` - Download resume
- `GET /api/files/profiles/<user_id>/` - Download profile picture

**Features:**
- **Authentication Required**: All downloads require authentication
- **Access Control**: Permission checks before download
- **Signed URLs**: Optional signed URLs for direct access
- **Streaming**: Direct file streaming for local storage
- **Redirect**: Automatic redirect to signed URLs for cloud storage

**Query Parameters:**
- `signed=true` - Return signed URL instead of streaming

---

## 🧹 File Cleanup & Management

### ✅ Automatic Cleanup

**Location**: `apps/jobs/signals.py`, `apps/accounts/signals.py`

**Features:**
- **Application Deletion**: Automatically deletes resume files when application is deleted
- **User Deletion**: Automatically deletes profile pictures when user is deleted
- **Signal-Based**: Uses Django signals for automatic cleanup

### ✅ Management Command

**Location**: `apps/core/management/commands/cleanup_old_files.py`

**Command**: `python manage.py cleanup_old_files`

**Options:**
- `--days N` - Delete files older than N days (default: 90)
- `--dry-run` - Show what would be deleted without deleting
- `--applications` - Clean up application files only
- `--profiles` - Clean up profile picture files only

**Usage:**
```bash
# Dry run to see what would be deleted
python manage.py cleanup_old_files --days 90 --dry-run

# Actually delete old files
python manage.py cleanup_old_files --days 90

# Clean up only application files
python manage.py cleanup_old_files --applications --days 30
```

### ✅ File Cleanup Utilities

**Location**: `apps/core/file_management.py` - `FileCleanup`

**Methods:**
- `cleanup_orphaned_files()` - Remove files not referenced in database
- `cleanup_old_files()` - Remove files from old records
- `delete_file_safely()` - Safely delete file with error handling

---

## ⚙️ Configuration

### Environment Variables

Add to `.env` file:

```env
# File Storage Backend (local, supabase)
FILE_STORAGE_BACKEND=supabase

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-key
SUPABASE_STORAGE_BUCKET=files

# File Processing
ENABLE_VIRUS_SCANNING=false
ENABLE_IMAGE_OPTIMIZATION=true
ENABLE_RESUME_PARSING=true
MAX_IMAGE_WIDTH=800
MAX_IMAGE_HEIGHT=800
IMAGE_QUALITY=85
```

### Supabase Setup

1. **Create Storage Bucket:**
   - Go to Supabase Dashboard → Storage
   - Create a new bucket (e.g., "files")
   - Set bucket to public or configure RLS policies

2. **Get Credentials:**
   - Project URL: Found in Project Settings
   - API Key: Found in Project Settings → API

3. **Configure Environment:**
   - Set `SUPABASE_URL` and `SUPABASE_KEY` in `.env`
   - Set `SUPABASE_STORAGE_BUCKET` to your bucket name

---

## 📊 Integration with Models

### Application Model

**Resume Upload:**
- Automatic processing on upload
- Virus scanning (if enabled)
- Resume parsing (if enabled)
- Metadata extraction

**File Path:**
- Format: `resumes/%Y/%m/%d/filename.pdf`
- Organized by date for easy management

### User Model

**Profile Picture Upload:**
- Automatic image optimization
- Thumbnail generation
- Format conversion

**File Path:**
- Format: `profiles/filename.jpg`
- Optimized for web delivery

---

## 🔐 Security Features

### ✅ Implemented Security Measures

1. **Access Control**: Role-based file access
2. **Virus Scanning**: Optional ClamAV integration
3. **File Validation**: Size and extension validation
4. **Signed URLs**: Time-limited secure access
5. **Authentication**: All downloads require authentication
6. **Secure Storage**: Cloud storage with proper permissions

### ✅ Best Practices

1. **File Size Limits**: Enforced at validation level
2. **Extension Validation**: Only allowed file types
3. **MIME Type Detection**: Additional security layer
4. **File Hashing**: SHA256 for deduplication and integrity
5. **Automatic Cleanup**: Prevents orphaned files
6. **Error Handling**: Graceful degradation if services unavailable

---

## 🚀 Usage Examples

### Upload Resume with Processing

```python
from apps.core.file_processing import process_uploaded_file

# Process uploaded file
result = process_uploaded_file(
    uploaded_file,
    file_type='resume',
    optimize_image=False
)

# Check if file is safe
if not result['is_safe']:
    # Handle infected file
    return error_response

# Use processed file
resume_text = result['resume_data'].get('text', '')
```

### Generate Secure Download URL

```python
from apps.core.storage import storage_manager

# Generate signed URL (expires in 1 hour)
signed_url = storage_manager.generate_signed_url(
    'resumes/2024/01/15/resume.pdf',
    expiration=3600
)
```

### Access File via Storage Manager

```python
from apps.core.storage import storage_manager

# Save file
file_path = storage_manager.save('path/to/file.pdf', file_content)

# Check if exists
if storage_manager.exists(file_path):
    # Get URL
    url = storage_manager.url(file_path)
    
    # Get size
    size = storage_manager.size(file_path)
```

---

## 📋 Dependencies

**Required Packages:**
- `storages` - Django storage backends
- `supabase` - Supabase Storage support
- `Pillow` - Image processing
- `pdf2image` - PDF thumbnail generation
- `PyPDF2` - PDF parsing
- `python-docx` - DOCX parsing
- `python-magic` - MIME type detection
- `pyclamd` - Virus scanning (optional)

**Installation:**
```bash
pip install -r requirements.txt
```

---

## ✅ Implementation Status

### Fully Implemented ✅

- ✅ Storage abstraction layer
- ✅ Supabase Storage integration
- ✅ Local storage fallback
- ✅ Resume parsing (PDF, DOCX)
- ✅ Image optimization
- ✅ PDF thumbnail generation
- ✅ File metadata extraction
- ✅ Virus scanning integration
- ✅ Secure file download URLs
- ✅ File access control
- ✅ Automatic file cleanup
- ✅ Management command for old file purging
- ✅ CDN support (via Supabase CDN)

### Ready for Production ✅

- ✅ Production-ready storage backends
- ✅ Comprehensive file processing
- ✅ Security measures in place
- ✅ Automated cleanup
- ✅ Error handling and fallbacks

---

## 🔮 Future Enhancements (Optional)

### Advanced Features
- File versioning
- Image CDN integration (Cloudinary, ImageKit)
- Advanced resume parsing (AI/ML)
- File preview generation
- Batch file processing
- File compression
- Watermarking

---

**Status**: ✅ **COMPLETE** - Comprehensive file upload enhancement system fully implemented and ready for production use!
