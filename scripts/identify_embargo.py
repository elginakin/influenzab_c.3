#!/usr/bin/env python3
"""
exclude_embargo.py

CLI tool to extract Isolate_Name values from an Excel file where Publishing_Embargo_Until is present,
and write those Isolate_Name values (one per line) to a TSV file.

Usage examples:
  python exclude_embargo.py -i input.xlsx -o exclude_embargo.tsv
  python exclude_embargo.py --input data.xls --sheet 0 --output out.tsv

Requirements:
  - Python 3.6+
  - pandas
  - For .xlsx files: openpyxl (pip install openpyxl)
  - For legacy .xls files: xlrd==1.2.0 (pip install xlrd==1.2.0)
"""

import argparse
import os
import sys
import pandas as pd

def parse_args():
    parser = argparse.ArgumentParser(
        prog="exclude_embargo.py",
        description=(
            "Extract Isolate_Name values from an Excel file where Publishing_Embargo_Until is present, "
            "and write them (one per line) to an output TSV file."
        ),
        epilog=(
            "Examples:\n"
            "  python exclude_embargo.py -i input.xlsx -o exclude_embargo.tsv\n"
            "  python exclude_embargo.py --input data.xls --sheet 0 --output out.tsv\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "-i", "--input", required=True, help="Path to input Excel file (.xls or .xlsx)."
    )
    parser.add_argument(
        "-o", "--output", required=True, help="Path to output TSV file to create (e.g. exclude_embargo.tsv)."
    )
    parser.add_argument(
        "-s", "--sheet", default=None,
        help="Optional sheet name or index to read (default: first sheet). Use sheet name or zero-based index."
    )

    return parser.parse_args()

def main():
    args = parse_args()

    input_path = args.input
    output_path = args.output
    sheet_arg = args.sheet

    # Validate input path
    if not os.path.isfile(input_path):
        sys.exit(f"Input file not found: {input_path}")

    # Prepare pandas read_excel kwargs
    read_kwargs = {}
    if sheet_arg is not None:
        # allow numeric index or name
        try:
            read_kwargs['sheet_name'] = int(sheet_arg)
        except ValueError:
            read_kwargs['sheet_name'] = sheet_arg

    # Read the Excel file
    try:
        df = pd.read_excel(input_path, **read_kwargs)
    except Exception as e:
        sys.exit(f"Failed to read Excel file '{input_path}': {e}")

    # Normalize column names: strip whitespace
    df.rename(columns={c: str(c).strip() for c in df.columns}, inplace=True)

    # Build case-insensitive mapping of column names
    col_map = {c.lower(): c for c in df.columns}

    if 'isolate_name' not in col_map:
        sys.exit("Input file does not contain an 'Isolate_Name' column (case-insensitive).")
    if 'publishing_embargo_until' not in col_map:
        sys.exit("Input file does not contain a 'Publishing_Embargo_Until' column (case-insensitive).")

    isolate_col = col_map['isolate_name']
    embargo_col = col_map['publishing_embargo_until']

    # Create a boolean mask where embargo column is non-empty (after stripping)
    # Convert to string, replace 'nan' produced by str() for NaN, strip whitespace
    embargo_series = df[embargo_col].astype(str).replace('nan', '').str.strip()
    mask = embargo_series.astype(bool)

    # Extract isolate names for masked rows
    isolates = df.loc[mask, isolate_col].astype(str).str.strip()

    # Remove empty names and duplicates while preserving order
    seen = set()
    out_list = []
    for name in isolates:
        if not name:
            continue
        if name not in seen:
            seen.add(name)
            out_list.append(name)

    # Ensure output directory exists
    out_dir = os.path.dirname(os.path.abspath(output_path))
    if out_dir and not os.path.exists(out_dir):
        try:
            os.makedirs(out_dir, exist_ok=True)
        except Exception as e:
            sys.exit(f"Failed to create output directory '{out_dir}': {e}")

    # Write to TSV (one value per line)
    try:
        with open(output_path, 'w', encoding='utf-8') as fout:
            for name in out_list:
                fout.write(name + "\n")
    except Exception as e:
        sys.exit(f"Failed to write output file '{output_path}': {e}")

    print(f"Wrote {len(out_list)} isolate name(s) to {output_path}")

if __name__ == "__main__":
    main()