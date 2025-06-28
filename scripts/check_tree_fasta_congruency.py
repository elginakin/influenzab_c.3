#!/usr/bin/env python3

import argparse
import re

def parse_args():
    parser = argparse.ArgumentParser(description="Check congruency between Newick tree tip names and FASTA headers.")
    parser.add_argument("-t", "--tree", required=True, help="Input tree file (Newick or Nexus).")
    parser.add_argument("-f", "--fasta", required=True, help="Input FASTA file.")
    parser.add_argument("-o", "--output", help="Optional output TSV report.")
    return parser.parse_args()

def extract_tree_tips(tree_text):
    tips = set()
    # Extract quoted tip names
    tips.update(re.findall(r"'([^']+)'", tree_text))
    # Extract unquoted tip names
    unquoted = re.findall(r'(?<=[\(\),\s])([^\':;\(\),\s]+)(?=[:;\),\s])', tree_text)
    tips.update([t for t in unquoted if t not in tips])
    return tips

def extract_fasta_headers(fasta_text):
    headers = set()
    for line in fasta_text.splitlines():
        if line.startswith(">"):
            headers.add(line[1:].strip())
    return headers

def write_report(filename, matched, only_in_tree, only_in_fasta):
    with open(filename, "w") as out:
        out.write("name\tstatus\n")
        for name in sorted(matched):
            out.write(f"{name}\tmatched\n")
        for name in sorted(only_in_tree):
            out.write(f"{name}\tonly_in_tree\n")
        for name in sorted(only_in_fasta):
            out.write(f"{name}\tonly_in_fasta\n")

def main():
    args = parse_args()

    with open(args.tree, "r") as t:
        tree_text = t.read()
    with open(args.fasta, "r") as f:
        fasta_text = f.read()

    tree_tips = extract_tree_tips(tree_text)
    fasta_headers = extract_fasta_headers(fasta_text)

    matched = tree_tips & fasta_headers
    only_in_tree = tree_tips - fasta_headers
    only_in_fasta = fasta_headers - tree_tips

    print("=== Tree vs FASTA Congruency Report ===")
    print(f"Total tips in tree:         {len(tree_tips)}")
    print(f"Total headers in FASTA:     {len(fasta_headers)}")
    print(f"Matched names:              {len(matched)}")
    print(f"Only in tree (not FASTA):   {len(only_in_tree)}")
    print(f"Only in FASTA (not tree):   {len(only_in_fasta)}")

    if only_in_tree:
        print("\n[!] Names only in tree:")
        for name in sorted(only_in_tree):
            print(f"  - {name}")

    if only_in_fasta:
        print("\n[!] Names only in FASTA:")
        for name in sorted(only_in_fasta):
            print(f"  - {name}")

    if args.output:
        write_report(args.output, matched, only_in_tree, only_in_fasta)
        print(f"\n[✓] TSV report written to {args.output}")

if __name__ == "__main__":
    main()
