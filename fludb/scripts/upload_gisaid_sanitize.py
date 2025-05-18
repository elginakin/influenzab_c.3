import argparse
import re
from Bio import SeqIO
import pandas as pd
import sqlite3

def format_date(date_str):
    if pd.isna(date_str):
        return None
    date_parts = date_str.split('-')
    if len(date_parts) == 1:
        return f"{date_parts[0]}-XX-XX"
    elif len(date_parts) == 2:
        return f"{date_parts[0]}-{date_parts[1]}-XX"
    elif len(date_parts) == 3:
        return date_str
    else:
        return None

def sanitize_sample_id(sample_id):
    # Keep only alphanumerics, underscores, and slashes
    return re.sub(r'[^\w/]', '', sample_id)

def sanitize_duplicates(conn):
    cursor = conn.cursor()
    print("\U0001F9FC Sanitizing: removing duplicate sample_IDs from GISAID...")
    cursor.execute("""
        DELETE FROM influenza_genomes
        WHERE sequence_ID NOT IN (
            SELECT sequence_ID FROM influenza_genomes
            WHERE database_origin = 'gisaid' AND sample_ID IS NOT NULL AND date IS NOT NULL
            GROUP BY sample_ID
            HAVING date = MAX(date)
        ) AND database_origin = 'gisaid' AND sample_ID IS NOT NULL
    """)
    conn.commit()
    print("✅ Sanitization complete: duplicate sample_IDs removed.")

def update_database(db_path, fasta_file, metadata_file, remove_duplicates=False, sanitize_names=False):
    segment_map = {
        "PB2": "pb2", "PB1": "pb1", "PA": "pa", "HA": "ha",
        "NP": "np", "NA": "na", "MP": "mp", "NS": "ns"
    }

    print("Database connection established.")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    database_origin = 'gisaid'

    print("Processing FASTA file...")
    fasta_records_inserted = 0
    fasta_records_skipped = 0

    for record in SeqIO.parse(fasta_file, "fasta"):
        header = record.id
        parts = [p.strip().replace(" ", "") for p in header.split("|")]
        if len(parts) != 4:
            print(f"⚠️  Skipping malformed header: {header}")
            fasta_records_skipped += 1
            continue

        isolate_id, sample_id, segment_label, _ = parts
        segment_name = segment_map.get(segment_label.upper())
        if not segment_name:
            print(f"⚠️  Unknown segment '{segment_label}' in header: {header}")
            fasta_records_skipped += 1
            continue

        if sanitize_names:
            sample_id = sanitize_sample_id(sample_id)  # Only sanitize sample_id here

        sequence = str(record.seq)

        try:
            cursor.execute(f'''
                INSERT INTO influenza_genomes (sequence_ID, sample_ID, {segment_name}, database_origin)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(sequence_ID) DO UPDATE SET
                    {segment_name} = excluded.{segment_name},
                    database_origin = excluded.database_origin
            ''', (isolate_id, sample_id, sequence, database_origin))
            fasta_records_inserted += 1
        except Exception as e:
            print(f"❌ Skipped record {header}: {e}")
            fasta_records_skipped += 1

    print(f"✅ FASTA file processed: {fasta_records_inserted} records inserted or updated, {fasta_records_skipped} skipped.")

    print("Processing metadata file...")
    metadata_records_inserted = 0
    metadata_records_skipped = 0
    metadata_df = pd.read_excel(metadata_file)

    for _, row in metadata_df.iterrows():
        seq_id = str(row['Isolate_Id']).strip().replace(" ", "")  # No sanitizing here
        isolate_name = str(row.get('Isolate_Name', '')).strip().replace(" ", "")  # No sanitizing here

        sample_id = str(row.get('Isolate_Name', '')).strip().replace(" ", "")
        if sanitize_names:
            sample_id = sanitize_sample_id(sample_id)  # Only sanitize sample_id

        subtype_column = str(row.get('Subtype', '')).strip()
        lineage_column = str(row.get('Lineage', '')).strip()

        if subtype_column.startswith("A"):
            virus_type = "InfluenzaA"
            subtype = subtype_column.split("/")[-1].strip()
        elif subtype_column.startswith("B"):
            virus_type = "InfluenzaB"
            subtype = lineage_column if lineage_column else None
        else:
            virus_type = None
            subtype = None

        collection_date = format_date(row.get('Collection_Date', None))
        passage_history = row.get('Passage_History', None)
        location = row.get('Location', None)
        age = row.get('Host_Age', None)
        age_unit = row.get('Host_Age_Unit', None)
        sex = row.get('Host_Gender', None)

        try:
            cursor.execute('''
                INSERT INTO influenza_genomes (sequence_ID, sample_ID, type, subtype, date, passage_history, location, database_origin, age, age_unit, sex)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(sequence_ID) DO UPDATE SET
                    sample_ID = COALESCE(?, sample_ID),
                    type = COALESCE(?, type),
                    subtype = COALESCE(?, subtype),
                    date = COALESCE(?, date),
                    passage_history = COALESCE(?, passage_history),
                    location = COALESCE(?, location),
                    database_origin = COALESCE(?, database_origin),
                    age = COALESCE(?, age),
                    age_unit = COALESCE(?, age_unit),
                    sex = COALESCE(?, sex)
            ''', (
                seq_id, sample_id, virus_type, subtype, collection_date, passage_history, location, database_origin, age, age_unit, sex,
                sample_id, virus_type, subtype, collection_date, passage_history, location, database_origin, age, age_unit, sex
            ))
            metadata_records_inserted += 1
        except Exception as e:
            print(f"❌ Skipped metadata for {seq_id}: {e}")
            metadata_records_skipped += 1

    print(f"✅ Metadata file processed: {metadata_records_inserted} records inserted or updated, {metadata_records_skipped} skipped.")

    conn.commit()
    print("✔️ Data committed to the database. Verifying total entries...")

    cursor.execute("SELECT COUNT(*) FROM influenza_genomes")
    total_records = cursor.fetchone()[0]
    print(f"📦 Total records in the database: {total_records}")

    if remove_duplicates:
        sanitize_duplicates(conn)

    conn.close()
    print("🔒 Database connection closed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload GISAID FASTA and metadata files to a SQLite database.")
    parser.add_argument('-d', '--db', required=True, help='Path to the SQLite database file.')
    parser.add_argument('-f', '--fasta', required=True, help='Path to the GISAID FASTA file.')
    parser.add_argument('-m', '--metadata', required=True, help='Path to the GISAID metadata XLS file.')
    parser.add_argument('--remove-duplicate-strains', action='store_true',
                        help='Remove duplicate sample_IDs from GISAID after upload.')
    parser.add_argument('--sanitize-names', action='store_true',
                        help='Sanitize sample_ID only (not sequence_ID or isolate_name).')

    args = parser.parse_args()

    update_database(
        db_path=args.db,
        fasta_file=args.fasta,
        metadata_file=args.metadata,
        remove_duplicates=args.remove_duplicate_strains,
        sanitize_names=args.sanitize_names
    )
