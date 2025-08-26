import os
import mimetypes
import hashlib
from werkzeug.utils import secure_filename
from flask import current_app
import magic


class FileUploadSecurity:
    """File upload security utilities"""
    
    # Allowed file extensions and MIME types
    ALLOWED_EXTENSIONS = {
        'image': {
            'extensions': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'],
            'mimetypes': [
                'image/jpeg', 'image/png', 'image/gif',
                'image/bmp', 'image/webp'
            ]
        },
        'document': {
            'extensions': ['.pdf', '.doc', '.docx', '.txt'],
            'mimetypes': [
                'application/pdf', 'application/msword',
                ('application/vnd.openxmlformats-officedocument.'
                 'wordprocessingml.document'),
                'text/plain'
            ]
        }
    }
    
    # Maximum file sizes (in bytes)
    MAX_FILE_SIZES = {
        'image': 5 * 1024 * 1024,    # 5MB for images
        'document': 10 * 1024 * 1024  # 10MB for documents
    }
    
    # Blocked file signatures (magic bytes)
    DANGEROUS_SIGNATURES = [
        b'\x4d\x5a',  # PE/EXE files
        b'\x7f\x45\x4c\x46',  # ELF executables
        b'\xca\xfe\xba\xbe',  # Java class files
        b'\x50\x4b\x03\x04',  # ZIP files (could contain malware)
        b'\x52\x61\x72\x21',  # RAR files
    ]
    
    @classmethod
    def validate_filename(cls, filename):
        """
        Validate and sanitize filename
        
        Args:
            filename: Original filename
            
        Returns:
            str: Sanitized filename
            
        Raises:
            ValueError: If filename is invalid
        """
        if not filename:
            raise ValueError("Filename is required")
        
        # Use werkzeug's secure_filename
        safe_filename = secure_filename(filename)
        
        if not safe_filename:
            raise ValueError("Invalid filename")
        
        # Additional checks
        if len(safe_filename) > 255:
            raise ValueError("Filename too long")
        
        # Check for reserved names (Windows)
        reserved_names = [
            'CON', 'PRN', 'AUX', 'NUL',
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8',
            'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7',
            'LPT8', 'LPT9'
        ]
        
        name_without_ext = os.path.splitext(safe_filename)[0].upper()
        if name_without_ext in reserved_names:
            raise ValueError("Reserved filename")
        
        return safe_filename
    
    @classmethod
    def validate_file_type(cls, filename, file_content,
                           allowed_category='image'):
        """
        Validate file type using multiple methods
        
        Args:
            filename: Filename
            file_content: File content (bytes)
            allowed_category: Category of allowed files
            
        Returns:
            bool: True if file type is allowed
            
        Raises:
            ValueError: If file type is not allowed
        """
        if allowed_category not in cls.ALLOWED_EXTENSIONS:
            raise ValueError(f"Unknown file category: {allowed_category}")
        
        allowed_config = cls.ALLOWED_EXTENSIONS[allowed_category]
        
        # Check file extension
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in allowed_config['extensions']:
            raise ValueError(f"File extension {file_ext} not allowed")
        
        # Check MIME type using python-magic (more reliable than mimetypes)
        try:
            mime_type = magic.from_buffer(file_content, mime=True)
        except Exception:
            # Fallback to mimetypes
            mime_type = mimetypes.guess_type(filename)[0]
        
        if mime_type not in allowed_config['mimetypes']:
            raise ValueError(f"File type {mime_type} not allowed")
        
        # Check for dangerous file signatures
        cls._check_file_signature(file_content)
        
        return True
    
    @classmethod
    def _check_file_signature(cls, file_content):
        """
        Check file signature for dangerous file types
        
        Args:
            file_content: File content (bytes)
            
        Raises:
            ValueError: If dangerous signature detected
        """
        if len(file_content) < 4:
            return
        
        for signature in cls.DANGEROUS_SIGNATURES:
            if file_content.startswith(signature):
                raise ValueError("Dangerous file signature detected")
    
    @classmethod
    def validate_file_size(cls, file_content, file_category='image'):
        """
        Validate file size
        
        Args:
            file_content: File content (bytes)
            file_category: Category of file
            
        Raises:
            ValueError: If file size exceeds limit
        """
        file_size = len(file_content)
        # 1MB default
        max_size = cls.MAX_FILE_SIZES.get(file_category, 1024 * 1024)
        
        if file_size > max_size:
            max_mb = max_size / (1024 * 1024)
            raise ValueError(f"File size exceeds {max_mb}MB limit")
    
    @classmethod
    def scan_for_malware_patterns(cls, file_content):
        """
        Basic malware pattern scanning
        
        Args:
            file_content: File content (bytes)
            
        Raises:
            ValueError: If suspicious patterns found
        """
        # Convert to string for pattern matching (with error handling)
        try:
            content_str = file_content.decode('utf-8', errors='ignore')
        except Exception:
            # If can't decode, skip text-based checks
            return
        
        # Suspicious patterns
        suspicious_patterns = [
            'eval(',
            'exec(',
            '<script',
            'javascript:',
            'vbscript:',
            'onload=',
            'onerror=',
            '<?php',
            '<%',
            'shell_exec',
            'system(',
            'passthru(',
        ]
        
        content_lower = content_str.lower()
        for pattern in suspicious_patterns:
            if pattern in content_lower:
                msg = f"Suspicious pattern found: {pattern}"
                current_app.logger.warning(msg)
                raise ValueError("Suspicious content detected")
    
    @classmethod
    def generate_safe_filename(cls, original_filename, user_id=None):
        """
        Generate a safe, unique filename
        
        Args:
            original_filename: Original filename
            user_id: User ID for uniqueness
            
        Returns:
            str: Safe, unique filename
        """
        # Validate original filename
        safe_name = cls.validate_filename(original_filename)
        
        # Get file extension
        name, ext = os.path.splitext(safe_name)
        
        # Create unique identifier
        import time
        timestamp = str(int(time.time()))
        user_part = f"_u{user_id}" if user_id else ""
        
        # Generate hash of original name for uniqueness
        name_hash = hashlib.md5(name.encode()).hexdigest()[:8]
        
        # Construct new filename
        new_filename = f"{name_hash}_{timestamp}{user_part}{ext}"
        
        return new_filename
    
    @classmethod
    def validate_upload(cls, file_obj, filename=None,
                        allowed_category='image', user_id=None):
        """
        Complete file upload validation
        
        Args:
            file_obj: File object or file content
            filename: Original filename
            allowed_category: Category of allowed files
            user_id: User ID for logging
            
        Returns:
            dict: Validation result with safe filename and file content
            
        Raises:
            ValueError: If validation fails
        """
        # Read file content
        if hasattr(file_obj, 'read'):
            file_content = file_obj.read()
            file_obj.seek(0)  # Reset file pointer
        else:
            file_content = file_obj
        
        if not file_content:
            raise ValueError("Empty file not allowed")
        
        # Use filename from file object if not provided
        if not filename and hasattr(file_obj, 'filename'):
            filename = file_obj.filename
        
        if not filename:
            raise ValueError("Filename is required")
        
        # Validate file size
        cls.validate_file_size(file_content, allowed_category)
        
        # Validate file type
        cls.validate_file_type(filename, file_content, allowed_category)
        
        # Scan for malware patterns
        cls.scan_for_malware_patterns(file_content)
        
        # Generate safe filename
        safe_filename = cls.generate_safe_filename(filename, user_id)
        
        current_app.logger.info(
            f"File upload validated: {filename} -> {safe_filename} "
            f"(user: {user_id}, size: {len(file_content)} bytes)"
        )
        
        return {
            'safe_filename': safe_filename,
            'original_filename': filename,
            'file_content': file_content,
            'file_size': len(file_content),
            'validated': True
        }
