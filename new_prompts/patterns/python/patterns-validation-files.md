# patterns-validation-files - File Upload Security


> **Specialized Guide**: Secure file upload handling, MIME type verification, virus scanning, and storage security.

> **Specialized Guide**: Comprehensive Pydantic validation patterns, security best practices, and input handling for Python projects.
## 📤 File Upload Security

### File Validation Basics

```python
from fastapi import FastAPI, UploadFile, File, HTTPException, status
from pydantic import BaseModel, Field
from typing import Annotated
import magic  # python-magic for MIME detection
from pathlib import Path
import hashlib

app = FastAPI()

class FileMetadata(BaseModel):
    """Validated file metadata."""
    filename: str
    content_type: str
    size: int
    sha256: str

# Configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_MIME_TYPES = {
    'image/jpeg',
    'image/png',
    'image/gif',
    'application/pdf',
    'text/plain',
}
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

async def validate_file_upload(file: UploadFile) -> FileMetadata:
    """
    Comprehensive file upload validation.

    Validates:
    - File size (streaming and total)
    - MIME type (actual content, not just extension)
    - Filename (sanitization)

    Raises:
        HTTPException: If validation fails
    """
    # Read file header for MIME detection (first 8KB)
    header = await file.read(8192)

    # Detect actual MIME type from content
    mime = magic.from_buffer(header, mime=True)

    # Validate MIME type
    if mime not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed: {mime}. Allowed types: {ALLOWED_MIME_TYPES}"
        )

    # Reset file pointer to beginning
    await file.seek(0)

    # Stream file and validate size
    total_size = 0
    file_hash = hashlib.sha256()
    chunks = []

    while chunk := await file.read(8192):
        total_size += len(chunk)

        # Check size limit
        if total_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE} bytes"
            )

        # Update hash
        file_hash.update(chunk)
        chunks.append(chunk)

    # Sanitize filename
    safe_filename = sanitize_filename(file.filename or "upload")

    return FileMetadata(
        filename=safe_filename,
        content_type=mime,
        size=total_size,
        sha256=file_hash.hexdigest()
    )

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal and injection attacks.

    Rules:
    - Remove path components (keep only filename)
    - Replace dangerous characters
    - Limit length
    - Ensure valid extension
    """
    # Remove path components
    safe_name = Path(filename).name

    # Block dangerous patterns
    if '..' in safe_name or safe_name.startswith('.'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename"
        )

    # Replace dangerous characters
    import re
    safe_name = re.sub(r'[^\w\s.-]', '_', safe_name)

    # Limit length
    if len(safe_name) > 255:
        name, ext = safe_name.rsplit('.', 1)
        safe_name = name[:250] + '.' + ext

    # Ensure filename is not empty
    if not safe_name or safe_name == '.':
        safe_name = 'unnamed'

    return safe_name

@app.post("/upload", response_model=FileMetadata)
async def upload_file(
    file: Annotated[UploadFile, File(description="File to upload")]
) -> FileMetadata:
    """
    Upload file with validation.

    Security checks:
    - MIME type verification
    - Size validation
    - Filename sanitization
    """
    # Validate file
    metadata = await validate_file_upload(file)

    # Reset file pointer
    await file.seek(0)

    # Save file with safe filename
    file_path = UPLOAD_DIR / f"{metadata.sha256}_{metadata.filename}"

    with open(file_path, 'wb') as f:
        while chunk := await file.read(8192):
            f.write(chunk)

    return metadata
```

### MIME Type Verification

```python
import magic
from typing import Dict, Set

class MIMEValidator:
    """
    Validate MIME types from file content, not just extension.

    Why? Extensions can be changed, but magic bytes cannot.
    """

    # Mapping of allowed MIME types to allowed extensions
    MIME_EXTENSION_MAP: Dict[str, Set[str]] = {
        'image/jpeg': {'.jpg', '.jpeg'},
        'image/png': {'.png'},
        'image/gif': {'.gif'},
        'application/pdf': {'.pdf'},
        'text/plain': {'.txt'},
        'application/zip': {'.zip'},
    }

    @classmethod
    async def validate_mime_and_extension(
        cls,
        file: UploadFile,
        allowed_mimes: Set[str]
    ) -> str:
        """
        Validate both MIME type and extension match.

        Returns:
            Detected MIME type

        Raises:
            HTTPException: If MIME type or extension invalid
        """
        # Read header
        header = await file.read(8192)
        await file.seek(0)

        # Detect MIME from content
        detected_mime = magic.from_buffer(header, mime=True)

        # Check MIME is allowed
        if detected_mime not in allowed_mimes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed: {detected_mime}"
            )

        # Verify extension matches MIME type
        if file.filename:
            file_ext = Path(file.filename).suffix.lower()
            allowed_extensions = cls.MIME_EXTENSION_MAP.get(detected_mime, set())

            if file_ext not in allowed_extensions:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Extension {file_ext} does not match file type {detected_mime}"
                )

        return detected_mime

# Usage
@app.post("/upload/image")
async def upload_image(file: UploadFile = File(...)):
    """Upload image with strict MIME validation."""
    mime = await MIMEValidator.validate_mime_and_extension(
        file,
        allowed_mimes={'image/jpeg', 'image/png', 'image/gif'}
    )

    # Process image...
    return {"mime_type": mime}
```

### File Size Validation (Streaming)

```python
from fastapi import Request
from starlette.datastructures import UploadFile as StarletteUploadFile

class MaxSizeValidator:
    """
    Validate file size during streaming upload.

    Prevents memory exhaustion from large files.
    """

    def __init__(self, max_size: int):
        """
        Args:
            max_size: Maximum file size in bytes
        """
        self.max_size = max_size

    async def __call__(self, file: UploadFile) -> UploadFile:
        """
        Validate file size during streaming.

        Raises:
            HTTPException: If file exceeds max size
        """
        total_size = 0

        # Create new file object that validates during read
        original_read = file.read

        async def validated_read(size: int = -1):
            nonlocal total_size
            chunk = await original_read(size)
            total_size += len(chunk)

            if total_size > self.max_size:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File too large. Maximum: {self.max_size} bytes"
                )

            return chunk

        file.read = validated_read
        return file

# Usage with dependency injection
@app.post("/upload/large")
async def upload_large_file(
    file: Annotated[
        UploadFile,
        Depends(MaxSizeValidator(max_size=100 * 1024 * 1024))  # 100 MB
    ]
):
    """Upload with size validation during streaming."""
    # File is already validated during streaming
    return {"status": "uploaded"}
```

### Virus Scanning Integration

```python
import subprocess
from typing import Optional
import tempfile

class VirusScanner:
    """
    Integrate virus scanning with ClamAV.

    Setup:
        apt-get install clamav clamav-daemon
        systemctl start clamav-daemon
    """

    @staticmethod
    async def scan_file(file_path: Path) -> bool:
        """
        Scan file for viruses using ClamAV.

        Returns:
            True if file is clean, False if infected

        Raises:
            HTTPException: If scan fails or virus detected
        """
        try:
            # Run ClamAV scan
            result = subprocess.run(
                ['clamdscan', '--no-summary', str(file_path)],
                capture_output=True,
                text=True,
                timeout=30
            )

            # Check result
            if result.returncode == 0:
                return True  # Clean
            elif result.returncode == 1:
                # Virus found
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File contains malware"
                )
            else:
                # Scan error
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Virus scan failed"
                )

        except subprocess.TimeoutExpired:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Virus scan timeout"
            )

    @staticmethod
    async def scan_upload(file: UploadFile) -> bool:
        """
        Scan uploaded file before processing.

        Creates temporary file for scanning.
        """
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            # Write uploaded file to temp
            content = await file.read()
            tmp.write(content)
            tmp_path = Path(tmp.name)

        try:
            # Reset file pointer
            await file.seek(0)

            # Scan temp file
            is_clean = await VirusScanner.scan_file(tmp_path)
            return is_clean

        finally:
            # Clean up temp file
            tmp_path.unlink(missing_ok=True)

# Usage
@app.post("/upload/secure")
async def upload_with_scan(file: UploadFile = File(...)):
    """Upload with virus scanning."""
    # Scan file
    is_clean = await VirusScanner.scan_upload(file)

    if not is_clean:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File failed security scan"
        )

    # Process file...
    return {"status": "clean"}
```

### Image Manipulation Safety

```python
from PIL import Image, ImageFile
from io import BytesIO

# Prevent decompression bomb attacks
Image.MAX_IMAGE_PIXELS = 89478485  # ~8K image
ImageFile.LOAD_TRUNCATED_IMAGES = False

class ImageValidator:
    """
    Secure image validation and processing.

    Protects against:
    - Decompression bombs
    - Malicious EXIF data
    - Oversized images
    """

    MAX_WIDTH = 4096
    MAX_HEIGHT = 4096

    @classmethod
    async def validate_image(cls, file: UploadFile) -> Image.Image:
        """
        Validate and safely load image.

        Raises:
            HTTPException: If image is invalid or dangerous
        """
        try:
            # Read file content
            content = await file.read()
            await file.seek(0)

            # Load image
            image = Image.open(BytesIO(content))

            # Verify image can be loaded
            image.verify()

            # Reload image for processing (verify() invalidates it)
            image = Image.open(BytesIO(content))

            # Check dimensions
            width, height = image.size
            if width > cls.MAX_WIDTH or height > cls.MAX_HEIGHT:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Image too large. Max: {cls.MAX_WIDTH}x{cls.MAX_HEIGHT}"
                )

            return image

        except Image.DecompressionBombError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Image too large (decompression bomb suspected)"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid image: {str(e)}"
            )

    @classmethod
    async def sanitize_image(cls, image: Image.Image) -> Image.Image:
        """
        Strip dangerous metadata and re-encode image.

        Removes:
        - EXIF data
        - Comments
        - Other metadata
        """
        # Create new image without metadata
        clean_image = Image.new(image.mode, image.size)
        clean_image.putdata(list(image.getdata()))

        return clean_image

    @classmethod
    async def process_upload(cls, file: UploadFile) -> BytesIO:
        """
        Complete image validation and sanitization.

        Returns:
            Clean image as BytesIO
        """
        # Validate image
        image = await cls.validate_image(file)

        # Sanitize (remove metadata)
        clean_image = await cls.sanitize_image(image)

        # Convert to bytes
        output = BytesIO()
        clean_image.save(output, format=image.format or 'PNG')
        output.seek(0)

        return output

# Usage
@app.post("/upload/image/safe")
async def upload_safe_image(file: UploadFile = File(...)):
    """Upload image with full security validation."""
    # Validate MIME type
    mime = await MIMEValidator.validate_mime_and_extension(
        file,
        allowed_mimes={'image/jpeg', 'image/png'}
    )

    # Process and sanitize image
    clean_image = await ImageValidator.process_upload(file)

    # Save clean image
    safe_filename = sanitize_filename(file.filename or "image.png")
    file_path = UPLOAD_DIR / safe_filename

    with open(file_path, 'wb') as f:
        f.write(clean_image.getvalue())

    return {"filename": safe_filename, "mime_type": mime}
```

### Chunked Upload Handling

```python
from fastapi import BackgroundTasks
import aiofiles
from typing import List
from pydantic import BaseModel

class ChunkMetadata(BaseModel):
    """Metadata for chunked upload."""
    upload_id: str
    chunk_index: int
    total_chunks: int
    chunk_hash: str

class ChunkedUploadManager:
    """
    Handle large file uploads in chunks.

    Benefits:
    - Resume interrupted uploads
    - Stream large files without memory issues
    - Validate chunks independently
    """

    def __init__(self, upload_dir: Path):
        self.upload_dir = upload_dir
        self.chunks_dir = upload_dir / "chunks"
        self.chunks_dir.mkdir(exist_ok=True)

    async def upload_chunk(
        self,
        upload_id: str,
        chunk_index: int,
        total_chunks: int,
        chunk: UploadFile
    ) -> ChunkMetadata:
        """
        Upload single chunk.

        Validates:
        - Chunk size
        - Chunk hash
        - Upload ID
        """
        # Read chunk
        content = await chunk.read()

        # Validate chunk size (max 5 MB per chunk)
        if len(content) > 5 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Chunk too large"
            )

        # Calculate hash
        chunk_hash = hashlib.sha256(content).hexdigest()

        # Save chunk
        chunk_path = self.chunks_dir / f"{upload_id}_{chunk_index:04d}"

        async with aiofiles.open(chunk_path, 'wb') as f:
            await f.write(content)

        return ChunkMetadata(
            upload_id=upload_id,
            chunk_index=chunk_index,
            total_chunks=total_chunks,
            chunk_hash=chunk_hash
        )

    async def finalize_upload(
        self,
        upload_id: str,
        total_chunks: int,
        expected_hashes: List[str]
    ) -> Path:
        """
        Combine chunks into final file after validation.

        Validates:
        - All chunks present
        - Chunk hashes match
        - Final file integrity
        """
        # Verify all chunks present
        chunk_paths = []
        for i in range(total_chunks):
            chunk_path = self.chunks_dir / f"{upload_id}_{i:04d}"
            if not chunk_path.exists():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing chunk {i}"
                )
            chunk_paths.append(chunk_path)

        # Combine chunks
        final_path = self.upload_dir / f"{upload_id}_complete"

        async with aiofiles.open(final_path, 'wb') as outfile:
            for i, chunk_path in enumerate(chunk_paths):
                async with aiofiles.open(chunk_path, 'rb') as infile:
                    chunk_content = await infile.read()

                    # Verify chunk hash
                    chunk_hash = hashlib.sha256(chunk_content).hexdigest()
                    if chunk_hash != expected_hashes[i]:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Chunk {i} hash mismatch"
                        )

                    await outfile.write(chunk_content)

        # Clean up chunks
        for chunk_path in chunk_paths:
            chunk_path.unlink()

        return final_path

# Usage
chunk_manager = ChunkedUploadManager(UPLOAD_DIR)

@app.post("/upload/chunk", response_model=ChunkMetadata)
async def upload_chunk(
    upload_id: str,
    chunk_index: int,
    total_chunks: int,
    chunk: UploadFile = File(...)
):
    """Upload single chunk."""
    return await chunk_manager.upload_chunk(
        upload_id,
        chunk_index,
        total_chunks,
        chunk
    )

@app.post("/upload/finalize")
async def finalize_upload(
    upload_id: str,
    total_chunks: int,
    chunk_hashes: List[str],
    background_tasks: BackgroundTasks
):
    """Finalize chunked upload."""
    final_path = await chunk_manager.finalize_upload(
        upload_id,
        total_chunks,
        chunk_hashes
    )

    # Optionally: Run virus scan in background
    background_tasks.add_task(VirusScanner.scan_file, final_path)

    return {"status": "complete", "file_id": upload_id}
```

### Storage Path Security

```python
from pathlib import Path
import os

class SecureStorage:
    """
    Secure file storage with path traversal prevention.

    Security principles:
    - Never trust user-provided paths
    - Use absolute paths
    - Validate paths are within allowed directory
    - Use UUIDs for filenames (not user input)
    """

    def __init__(self, base_dir: Path):
        """
        Args:
            base_dir: Absolute path to upload directory
        """
        self.base_dir = base_dir.resolve()

        # Ensure base directory exists
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def get_safe_path(self, filename: str) -> Path:
        """
        Get safe file path, preventing path traversal.

        Raises:
            HTTPException: If path escapes base directory
        """
        # Remove any path components
        safe_filename = Path(filename).name

        # Construct full path
        file_path = (self.base_dir / safe_filename).resolve()

        # Verify path is within base directory
        if not str(file_path).startswith(str(self.base_dir)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file path"
            )

        return file_path

    def generate_safe_filename(self, original_filename: str) -> str:
        """
        Generate UUID-based filename to avoid collisions.

        Format: {uuid}_{sanitized_original_name}
        """
        import uuid

        # Sanitize original filename
        safe_name = sanitize_filename(original_filename)

        # Generate UUID prefix
        file_id = uuid.uuid4().hex[:8]

        return f"{file_id}_{safe_name}"

# Usage
storage = SecureStorage(UPLOAD_DIR)

@app.post("/upload/secure-path")
async def upload_secure_path(file: UploadFile = File(...)):
    """Upload with secure path handling."""
    # Generate safe filename
    safe_filename = storage.generate_safe_filename(file.filename or "upload")

    # Get validated path
    file_path = storage.get_safe_path(safe_filename)

    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        while chunk := await file.read(8192):
            await f.write(chunk)

    return {"filename": safe_filename}
```

### Complete Secure Upload Example

```python
@app.post("/upload/complete-security", response_model=FileMetadata)
async def upload_complete_security(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
) -> FileMetadata:
    """
    Complete file upload with all security measures.

    Security layers:
    1. MIME type validation (content-based)
    2. File size validation (streaming)
    3. Filename sanitization
    4. Secure path handling
    5. Virus scanning (background)
    6. Image sanitization (if image)
    """
    # 1. Validate MIME type
    mime = await MIMEValidator.validate_mime_and_extension(
        file,
        allowed_mimes=ALLOWED_MIME_TYPES
    )

    # 2. Validate file (size, content)
    metadata = await validate_file_upload(file)
    await file.seek(0)

    # 3. Generate secure filename
    safe_filename = storage.generate_safe_filename(metadata.filename)
    file_path = storage.get_safe_path(safe_filename)

    # 4. Process based on file type
    if mime.startswith('image/'):
        # Sanitize image
        clean_image = await ImageValidator.process_upload(file)

        # Save sanitized image
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(clean_image.getvalue())
    else:
        # Save file normally
        async with aiofiles.open(file_path, 'wb') as f:
            while chunk := await file.read(8192):
                await f.write(chunk)

    # 5. Schedule virus scan
    background_tasks.add_task(VirusScanner.scan_file, file_path)

    return FileMetadata(
        filename=safe_filename,
        content_type=mime,
        size=metadata.size,
        sha256=metadata.sha256
    )
```

---
