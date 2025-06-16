import argparse
import os
import shutil

def ignore_dirs(dir, files, exclude_dirs):
    # Only ignore directories in the exclude_dirs list
    ignored = []
    for f in files:
        if f in exclude_dirs:
            ignored.append(f)
    return set(ignored)

def copy_project(src_dir, dest_dir, exclude_dirs=None):
    if exclude_dirs is None:
        exclude_dirs = []
    src_dir = os.path.abspath(src_dir)
    dest_dir = os.path.abspath(dest_dir)
    os.makedirs(dest_dir, exist_ok=True)
    for item in os.listdir(src_dir):
        if item in exclude_dirs:
            continue
        s = os.path.join(src_dir, item)
        d = os.path.join(dest_dir, item)
        if os.path.isdir(s):
            shutil.copytree(
                s, d, 
                ignore=lambda dir, files: ignore_dirs(dir, files, exclude_dirs),
                dirs_exist_ok=True,
                symlinks=True,
                copy_function=shutil.copy2,
                ignore_dangling_symlinks=True
            )
        else:
            try:
                shutil.copy2(s, d)
            except PermissionError:
                print(f"Permission denied: {s} (skipped)")

def main():
    parser = argparse.ArgumentParser(description="Copy project directory, excluding specified subdirectories.")
    parser.add_argument('-s', '--src', required=True, help='Path to the source project directory')
    parser.add_argument('-o', '--out', required=True, help='Path to the output backup directory')
    parser.add_argument('--exclude', nargs='*', default=['snapshots', 'nextstrain_snapshots'], help='Subdirectories to exclude (default: snapshots, nextstrain_snapshots)')
    args = parser.parse_args()
    copy_project(args.src, args.out, exclude_dirs=args.exclude)
    print(f"Project copied from {args.src} to {args.out}, excluding: {', '.join(args.exclude)}")

if __name__ == "__main__":
    main()