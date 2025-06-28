#!/usr/bin/env python3
import argparse
import os
import shutil


def copy_project(src_dir, dest_dir, exclude_dirs=None):
    if exclude_dirs is None:
        exclude_dirs = []
    src_dir = os.path.abspath(src_dir)
    dest_dir = os.path.abspath(dest_dir)
    # Ensure output directory exists
    os.makedirs(dest_dir, exist_ok=True)
    for item in os.listdir(src_dir):
        s = os.path.join(src_dir, item)
        d = os.path.join(dest_dir, item)
        # Exclude specified directories
        if os.path.basename(s) in exclude_dirs:
            continue
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)


def main():
    parser = argparse.ArgumentParser(description="Copy project directory, excluding specified subdirectories.")
    parser.add_argument('-s', '--src', required=True, help='Path to the source project directory')
    parser.add_argument('-o', '--out', required=True, help='Path to the output backup directory')
    parser.add_argument('--exclude', nargs='*', default=['snapshots'], help='Subdirectories to exclude (default: snapshots)')
    args = parser.parse_args()
    copy_project(args.src, args.out, exclude_dirs=args.exclude)
    print(f"Project copied from {args.src} to {args.out}, excluding: {', '.join(args.exclude)}")

if __name__ == "__main__":
    main()
