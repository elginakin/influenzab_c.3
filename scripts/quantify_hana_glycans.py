#!/usr/bin/env python3

import argparse
import pandas as pd

def count_glycans(entry: str, valid_prefixes: list) -> int:
    """
    Counts the number of glycan motifs starting with any of the valid prefixes.
    """
    if pd.isna(entry) or entry.strip() == "":
        return 0
    return sum(1 for part in entry.split(";") if any(part.startswith(prefix) for prefix in valid_prefixes))

def main():
    parser = argparse.ArgumentParser(description="Count HA and NA N-glycosylation sites from TSV input.")
    parser.add_argument("-i", "--input", required=True, help="Input TSV file with ha and na glycosylation columns present")
    parser.add_argument("-o", "--output", required=True, help="Output TSV file")
    parser.add_argument("-ha", "--ha_col", required=True, help="Column name for HA glycosylation")
    parser.add_argument("-na", "--na_col", required=True, help="Column name for NA glycosylation")

    args = parser.parse_args()

    # Read input file
    df = pd.read_csv(args.input, sep="\t")

    # Define acceptable prefixes
    ha_prefixes = ["HA1:", "HA2:"]
    na_prefixes = ["NA:"]

    # Count glycans
    df["ha_total_nglycans"] = df[args.ha_col].apply(lambda x: count_glycans(x, ha_prefixes))
    df["na_total_nglycans"] = df[args.na_col].apply(lambda x: count_glycans(x, na_prefixes))

    # Write output
    df.to_csv(args.output, sep="\t", index=False)

if __name__ == "__main__":
    main()
