"""
File Cleanup Utility - Prevents Folder Clutter

This manages old files in uploads/ and outputs/ folders.
You can set how long to keep files before auto-deleting them.
"""

import os
import time
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta

from src.core.config import Config


class FileCleanup:
    """
    Manages file cleanup in uploads and outputs folders
    
    Simple explanation:
    - Deletes files older than a certain age
    - Prevents folders from getting too full
    - Can be run automatically or manually
    """
    
    def __init__(self, 
                 max_age_hours: int = 24,
                 keep_recent: int = 10):
        """
        Initialize cleanup utility
        
        Args:
            max_age_hours: Delete files older than this many hours (default: 24)
            keep_recent: Always keep this many most recent files (default: 10)
        """
        self.max_age_hours = max_age_hours
        self.keep_recent = keep_recent
    
    def cleanup_uploads(self, dry_run: bool = False) -> int:
        """
        Clean up old files in uploads folder
        
        Args:
            dry_run: If True, just report what would be deleted without deleting
        
        Returns:
            Number of files deleted (or would be deleted)
        """
        return self._cleanup_folder(Config.UPLOAD_FOLDER, dry_run)
    
    def cleanup_outputs(self, dry_run: bool = False) -> int:
        """
        Clean up old files in outputs folder
        
        Args:
            dry_run: If True, just report what would be deleted without deleting
        
        Returns:
            Number of files deleted (or would be deleted)
        """
        return self._cleanup_folder(Config.OUTPUT_FOLDER, dry_run)
    
    def _cleanup_folder(self, folder_path: str, dry_run: bool = False) -> int:
        """Clean up files in a specific folder"""
        folder = Path(folder_path)
        if not folder.exists():
            return 0
        
        files = []
        cutoff_time = time.time() - (self.max_age_hours * 3600)
        
        # Get all files with their modification times
        for file_path in folder.iterdir():
            if file_path.is_file():
                mtime = file_path.stat().st_mtime
                files.append((mtime, file_path))
        
        # Sort by modification time (newest first)
        files.sort(reverse=True)
        
        deleted_count = 0
        
        # Keep the most recent N files
        for i, (mtime, file_path) in enumerate(files):
            if i < self.keep_recent:
                # Keep this file (it's in the top N most recent)
                continue
            
            if mtime < cutoff_time:
                # File is old enough to delete
                if not dry_run:
                    try:
                        file_path.unlink()
                        deleted_count += 1
                    except Exception as e:
                        print(f"⚠️  Could not delete {file_path.name}: {e}")
                else:
                    deleted_count += 1
        
        return deleted_count
    
    def cleanup_all(self, dry_run: bool = False) -> dict:
        """
        Clean up both uploads and outputs folders
        
        Returns:
            Dictionary with cleanup results
        """
        uploads_deleted = self.cleanup_uploads(dry_run)
        outputs_deleted = self.cleanup_outputs(dry_run)
        
        return {
            'uploads_deleted': uploads_deleted,
            'outputs_deleted': outputs_deleted,
            'total_deleted': uploads_deleted + outputs_deleted
        }
    
    def get_folder_stats(self) -> dict:
        """Get statistics about files in uploads and outputs folders"""
        stats = {}
        
        for folder_name, folder_path in [
            ('uploads', Config.UPLOAD_FOLDER),
            ('outputs', Config.OUTPUT_FOLDER)
        ]:
            folder = Path(folder_path)
            if not folder.exists():
                stats[folder_name] = {'count': 0, 'size_mb': 0}
                continue
            
            files = list(folder.iterdir())
            file_count = len([f for f in files if f.is_file()])
            total_size = sum(f.stat().st_size for f in files if f.is_file())
            
            stats[folder_name] = {
                'count': file_count,
                'size_mb': round(total_size / (1024 * 1024), 2)
            }
        
        return stats

