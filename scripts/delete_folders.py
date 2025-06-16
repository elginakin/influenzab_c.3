#!/usr/bin/env python3
import argparse
import os
import shutil
import datetime
import re


def prompt_yes(question):
    while True:
        reply = input(f"{question} [Yes]: ").strip()
        if reply == "Yes":
            return True
        else:
            print("Please type exactly 'Yes' (case sensitive) to proceed.")
            return False

def prompt_exact_text(required_text):
    reply = input(f"Please type the following: \"{required_text}\": ").strip()
    return reply == required_text

def check_todays_snapshot():
    today = datetime.datetime.now().strftime("%Y%m%d")
    snapshots_dir = "snapshots"
    if not os.path.exists(snapshots_dir):
        print(f"Error: {snapshots_dir} directory does not exist.")
        return False
    
    today_pattern = re.compile(today)
    found = False
    for item in os.listdir(snapshots_dir):
        full_path = os.path.join(snapshots_dir, item)
        if os.path.isdir(full_path) and today_pattern.match(item):
            print(f"Found today's snapshot: {full_path}")
            found = True
            break
            
    if not found:
        print(f"Error: No snapshot for today ({today}) found in {snapshots_dir}/")
        print("Please create a backup before proceeding.")
    
    return found

def delete_folder(path):
    if os.path.exists(path):
        shutil.rmtree(path)
        print(f"Deleted: {path}")
    else:
        print(f"Not found (skipped): {path}")

def main():
    parser = argparse.ArgumentParser(description="Delete specified project folders after user confirmation.")
    parser.add_argument('--data', default='data', help='Path to the data directory (default: data)')
    parser.add_argument('--results', default='results', help='Path to the results directory (default: results)')
    parser.add_argument('--intermediate', default='source/intermediate', help='Path to the intermediate directory (default: source/intermediate)')
    args = parser.parse_args()

    print("WARNING: This will permanently delete the following folders and all their contents:")
    print(f"  - {args.data}\n  - {args.results}\n  - {args.intermediate}\n")
    
    # Check for "Yes" and verify today's snapshot exists
    if not prompt_yes("Are all files currently backed up in the snapshots/ folder?"):
        print("Aborting. Please back up your files before deleting.")
        return
    
    # Check for today's snapshot
    if not check_todays_snapshot():
        return
        
    # Prompt for exact text
    if not prompt_exact_text("Let Gemma into the pond"):
        print("Text did not match. Aborting deletion for safety.")
        return

    delete_folder(args.data)
    delete_folder(args.results)
    delete_folder(args.intermediate)
    print("Done.")

if __name__ == "__main__":
    main()
