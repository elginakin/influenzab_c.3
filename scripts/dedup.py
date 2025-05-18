import argparse
import csv
import logging
import os
from collections import defaultdict

def setup_logger():
    log_file = "dedup_strains.log"
    logging.basicConfig(
        filename=log_file,
        filemode='w',
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    return log_file

def deduplicate_tsv(input_path, output_path, dedup_col, duplicates_path=None, drop_all_duplicates=False):
    rows_by_value = defaultdict(list)

    with open(input_path, 'r', newline='') as infile:
        reader = csv.DictReader(infile, delimiter='\t')
        header = reader.fieldnames

        if dedup_col not in header:
            msg = f"Column '{dedup_col}' not found in input file."
            logging.error(msg)
            raise ValueError(msg)

        for row in reader:
            value = row[dedup_col]
            rows_by_value[value].append(row)

    deduplicated_rows = []
    duplicate_rows = []

    for value, rows in rows_by_value.items():
        if len(rows) == 1:
            deduplicated_rows.append(rows[0])
        else:
            duplicate_rows.extend(rows)
            if not drop_all_duplicates:
                deduplicated_rows.append(rows[0])

    with open(output_path, 'w', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=header, delimiter='\t')
        writer.writeheader()
        writer.writerows(deduplicated_rows)

    if duplicates_path:
        with open(duplicates_path, 'w', newline='') as dupfile:
            writer = csv.DictWriter(dupfile, fieldnames=header, delimiter='\t')
            writer.writeheader()
            writer.writerows(duplicate_rows)

    # Logging and printing
    print(f"✅ Deduplication complete")
    print(f"🔍 Column used for deduplication: {dedup_col}")
    print(f"🧬 Duplicate records {'excluded entirely' if drop_all_duplicates else 'removed (keeping one)'}: {len(duplicate_rows)}")
    print(f"💾 Deduplicated output written to: {output_path}")
    logging.info(f"Column used for deduplication: {dedup_col}")
    logging.info(f"Drop all duplicates flag: {drop_all_duplicates}")
    logging.info(f"Duplicate records removed: {len(duplicate_rows)}")
    logging.info(f"Deduplicated output written to: {output_path}")

    if duplicates_path:
        print(f"📁 Duplicate records written to: {duplicates_path}")
        logging.info(f"Duplicate records written to: {duplicates_path}")

def main():
    parser = argparse.ArgumentParser(
        description="Deduplicate records in a TSV file by a specified column."
    )
    parser.add_argument(
        "-i", "--input", required=True, help="Path to input TSV file"
    )
    parser.add_argument(
        "-o", "--output", required=True, help="Path to output deduplicated TSV file"
    )
    parser.add_argument(
        "-c", "--dedup-col", required=True, help="Column name to deduplicate by (e.g. 'sample_ID')"
    )
    parser.add_argument(
        "-d", "--duplicates", required=False, help="Optional path to write duplicated records"
    )
    parser.add_argument(
        "--drop-all-duplicates", action="store_true",
        help="If set, remove all records with duplicated values in the deduplication column"
    )

    args = parser.parse_args()

    log_file = setup_logger()
    logging.info("Started deduplication process")

    try:
        deduplicate_tsv(
            args.input,
            args.output,
            args.dedup_col,
            args.duplicates,
            args.drop_all_duplicates
        )
    except Exception as e:
        print(f"❌ Error: {e}")
        logging.error(f"Error during deduplication: {e}")

    print(f"📝 Log written to: {log_file}")

if __name__ == "__main__":
    main()
