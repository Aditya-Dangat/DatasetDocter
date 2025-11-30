#!/usr/bin/env python3
"""
Manual File Cleanup Script

Run this to clean up old files in uploads/ and outputs/ folders.

Usage:
    python3 cleanup_files.py              # Clean up old files
    python3 cleanup_files.py --dry-run    # See what would be deleted
    python3 cleanup_files.py --stats      # Show folder statistics
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils.cleanup import FileCleanup
from src.core.config import Config


def main():
    parser = argparse.ArgumentParser(description='Clean up old files in uploads and outputs folders')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be deleted without actually deleting')
    parser.add_argument('--stats', action='store_true',
                       help='Show folder statistics')
    parser.add_argument('--max-age-hours', type=int, default=Config.CLEANUP_MAX_AGE_HOURS,
                       help=f'Hours before files are considered old (default: {Config.CLEANUP_MAX_AGE_HOURS})')
    parser.add_argument('--keep-recent', type=int, default=Config.CLEANUP_KEEP_RECENT,
                       help=f'Number of most recent files to always keep (default: {Config.CLEANUP_KEEP_RECENT})')
    
    args = parser.parse_args()
    
    cleanup = FileCleanup(
        max_age_hours=args.max_age_hours,
        keep_recent=args.keep_recent
    )
    
    if args.stats:
        # Show statistics
        stats = cleanup.get_folder_stats()
        print("\n📊 Folder Statistics")
        print("=" * 50)
        for folder_name, folder_stats in stats.items():
            print(f"\n{folder_name.upper()}/")
            print(f"  Files: {folder_stats['count']}")
            print(f"  Size: {folder_stats['size_mb']} MB")
        print()
        return
    
    # Perform cleanup
    mode = "DRY RUN" if args.dry_run else "CLEANUP"
    print(f"\n🧹 {mode} - Old Files")
    print("=" * 50)
    
    result = cleanup.cleanup_all(dry_run=args.dry_run)
    
    print(f"\n📁 Uploads folder:")
    print(f"   {'Would delete' if args.dry_run else 'Deleted'}: {result['uploads_deleted']} files")
    
    print(f"\n📁 Outputs folder:")
    print(f"   {'Would delete' if args.dry_run else 'Deleted'}: {result['outputs_deleted']} files")
    
    print(f"\n✅ Total: {result['total_deleted']} files {'would be deleted' if args.dry_run else 'deleted'}")
    
    if args.dry_run:
        print("\n💡 Run without --dry-run to actually delete these files")
    
    print()


if __name__ == '__main__':
    main()

