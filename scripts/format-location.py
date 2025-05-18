#!/usr/bin/env python3

"""
Command-line tool to split a hierarchical location column in a TSV file into:
region, country, division, and location (formerly 'location_detailed').

Assumes GISAID formating: Region / Country / Division / Location

The original location column is removed after parsing.

Usage:
    python format-location.py -i input.tsv -o output.tsv
    python format-location.py -i input.tsv -o output.tsv --location-column location_col_name (default: 'location')

"""

import argparse
import pandas as pd

def split_location(df, location_col="location"):
    """
    Splits a location column formatted like 'Region / Country / Division / Location' into separate columns.

    Parameters:
        df (pd.DataFrame): Input dataframe containing a location column.
        location_col (str): Name of the column to split (default: "location").

    Returns:
        pd.DataFrame: DataFrame with new columns: region, country, division, location.
                      The original location column is removed.
    """

    def extract_levels(value, level):
        if isinstance(value, str):
            parts = value.split(" / ")
            return parts[level] if len(parts) > level else None
        return None

    # Create new columns based on each hierarchical level
    df["region"] = df[location_col].apply(lambda x: extract_levels(x, 0))
    df["country"] = df[location_col].apply(lambda x: extract_levels(x, 1))
    df["division"] = df[location_col].apply(lambda x: extract_levels(x, 2))
    df["area"] = df[location_col].apply(lambda x: extract_levels(x, 3))

    # Drop the original combined location column
    df = df.drop(columns=[location_col])

    return df

def main():
    # Define CLI arguments
    parser = argparse.ArgumentParser(description="Split a location column into region, country, division, and location.")
    parser.add_argument("-i", "--input", required=True, help="Path to input TSV file")
    parser.add_argument("-o", "--output", required=True, help="Path to output TSV file")
    parser.add_argument("--location-column", default="location", help="Name of the column containing location data (default: 'location')")

    args = parser.parse_args()

    # Read input TSV
    df = pd.read_csv(args.input, sep="\t")

    # Check that the location column exists
    if args.location_column not in df.columns:
        raise ValueError(f"Column '{args.location_column}' not found in the input file.")

    # Apply splitting function
    df = split_location(df, location_col=args.location_column)

    # Save output TSV
    df.to_csv(args.output, sep="\t", index=False)

if __name__ == "__main__":
    main()
