#!/usr/bin/env python3

import argparse
import csv
import re

def parse_args():
    parser = argparse.ArgumentParser(description="Rename phylogenetic tree tips using metadata date info.")
    parser.add_argument("-t", "--tree", required=True, help="Input tree file (Newick or Nexus).")
    parser.add_argument("-m", "--metadata", required=True, help="Metadata file (TSV format).")
    parser.add_argument("--strain-column", required=True, help="Column name in metadata matching tip names.")
    parser.add_argument("--date-column", required=True, help="Column name in metadata with date (YYYY-MM-DD or partial).")
    parser.add_argument("-o", "--output", required=True, help="Output tree file with renamed tips.")
    parser.add_argument("--delimiter", default="|", help="Delimiter between strain name and date (default: '|').")
    parser.add_argument("--verbosity", type=int, choices=[0, 1, 2], default=1,
                        help="Verbosity level: 0 (silent), 1 (summary), 2 (detailed).")
    parser.add_argument("--strip-quotes", action="store_true",
                        help="Remove single quotes around tip names in the final output tree.")
    parser.add_argument("-f", "--fasta", help="Input FASTA file with headers to rename.")
    parser.add_argument("-O", "--fasta-output", help="Output FASTA file with renamed headers.")
    return parser.parse_args()

def build_rename_dict(metadata_file, strain_col, date_col, delimiter, verbosity):
    rename_dict = {}
    with open(metadata_file, newline='') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            strain = row.get(strain_col, "").strip()
            date = row.get(date_col, "").strip()
            if strain and date:
                rename_dict[strain] = f"{strain}{delimiter}{date}"
    if verbosity >= 1:
        print(f"[INFO] Found {len(rename_dict)} unique strains with dates in metadata.")
    return rename_dict

def extract_tips(tree_text):
    tips = set()

    # 1. Extract all single-quoted names first (e.g., 'B/Austria/...')
    quoted_matches = re.findall(r"'([^']+)'", tree_text)
    tips.update(quoted_matches)

    # 2. Then extract unquoted names (fallback) — but avoid duplicates
    unquoted_matches = re.findall(r'(?<=[\(\),\s])([^\':;\(\),\s]+)(?=[:;\),\s])', tree_text)
    tips.update([t for t in unquoted_matches if t not in tips])

    return tips

def rename_tree_tips(tree_text, rename_dict, verbosity):
    tips_in_tree = extract_tips(tree_text)
    matched = 0
    skipped = 0
    skipped_tips = []

    if verbosity >= 1:
        print(f"[INFO] Found {len(tips_in_tree)} unique tip names in tree.")

    for tip in sorted(tips_in_tree, key=len, reverse=True):
        if tip in rename_dict:
            new_name = rename_dict[tip]

            escaped_tip = re.escape(tip)
            escaped_new = new_name

            # Replace quoted tip: 'tip'
            tree_text, q_subs = re.subn(
                rf"(?<=[\(\),\s])'{escaped_tip}'(?=[:;\),\s])",
                f"'{escaped_new}'",
                tree_text
            )

            # Replace unquoted tip
            tree_text, u_subs = re.subn(
                rf"(?<=[\(\),\s]){escaped_tip}(?=[:;\),\s])",
                escaped_new,
                tree_text
            )

            if q_subs + u_subs > 0:
                matched += 1
        else:
            skipped += 1
            skipped_tips.append(tip)
            if verbosity == 2:
                print(f"[SKIP] {tip} not found in metadata.")

    if verbosity >= 1:
        percent = (matched / len(tips_in_tree)) * 100 if tips_in_tree else 0
        print(f"[SUMMARY] Renamed {matched} of {len(tips_in_tree)} tips ({percent:.1f}%).")

    if verbosity >= 1 and skipped_tips:
        print(f"[INFO] Skipped {len(skipped_tips)} tip(s) not found in metadata:")
        for tip in skipped_tips:
            print(f"  - {tip}")

    return tree_text

def rename_fasta_headers(fasta_text, rename_dict, verbosity):
    renamed_lines = []
    matched = 0
    skipped = 0
    skipped_headers = []

    for line in fasta_text.splitlines():
        if line.startswith(">"):
            original_name = line[1:].strip()
            if original_name in rename_dict:
                new_name = rename_dict[original_name]
                renamed_lines.append(f">{new_name}")
                matched += 1
            else:
                renamed_lines.append(line)
                skipped += 1
                skipped_headers.append(original_name)
                if verbosity == 2:
                    print(f"[SKIP] {original_name} not found in metadata.")
        else:
            renamed_lines.append(line)

    if verbosity >= 1:
        total = matched + skipped
        percent = (matched / total) * 100 if total else 0
        print(f"[SUMMARY] Renamed {matched} of {total} FASTA headers ({percent:.1f}%).")

    if verbosity >= 1 and skipped_headers:
        print(f"[INFO] Skipped {len(skipped_headers)} FASTA headers not found in metadata:")
        for name in skipped_headers:
            print(f"  - {name}")

    return "\n".join(renamed_lines) + "\n"

def main():
    args = parse_args()

    rename_dict = build_rename_dict(
        args.metadata,
        args.strain_column,
        args.date_column,
        args.delimiter,
        args.verbosity
    )

    with open(args.tree, "r") as infile:
        tree_text = infile.read()

    renamed_tree = rename_tree_tips(tree_text, rename_dict, args.verbosity)

    if args.strip_quotes:
        renamed_tree = re.sub(r"'([^']+)'", r"\1", renamed_tree)
        if args.verbosity >= 1:
            print("[INFO] Stripped quotes from final output tree.")

    with open(args.output, "w") as outfile:
        outfile.write(renamed_tree)

    if args.verbosity >= 0:
        print(f"[DONE] Renamed tree written to {args.output}")

    if args.fasta and args.fasta_output:
        if args.verbosity >= 1:
            print(f"[INFO] Renaming headers in FASTA file: {args.fasta}")
        with open(args.fasta, "r") as fin:
            fasta_text = fin.read()

        renamed_fasta = rename_fasta_headers(fasta_text, rename_dict, args.verbosity)

        with open(args.fasta_output, "w") as fout:
            fout.write(renamed_fasta)

        if args.verbosity >= 0:
            print(f"[DONE] Renamed FASTA written to {args.fasta_output}")

if __name__ == "__main__":
    main()
