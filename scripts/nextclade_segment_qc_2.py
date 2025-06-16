import subprocess
import pandas as pd
from pathlib import Path
from functools import reduce

# Define constants
segments = ['pb2', 'pb1', 'pa', 'ha', 'np', 'na', 'mp', 'ns']
input_base = Path("source/intermediate/vic")
nextclade_dataset_base = Path("nextclade/flu/vic")
output_metadata_name = "metadata_qc.tsv"

def run_nextclade(segment):
    input_fasta = input_base / segment / "sequences.fasta"
    output_tsv = input_base / segment / "nextclade.tsv"
    dataset_dir = nextclade_dataset_base / segment

    print(f"🔁 Running Nextclade for {segment}...")
    subprocess.run([
        "nextclade", "run",
        "-D", str(dataset_dir),
        "-t", str(output_tsv),
        str(input_fasta)
    ], check=True)
    print(f"✅ Completed Nextclade for {segment}")

def extract_qc_data(segment):
    df = pd.read_csv(input_base / segment / "nextclade.tsv", sep="\t", low_memory=False)

    # Extract common QC columns
    df_segment = df[["seqName", "qc.overallScore", "qc.overallStatus", "coverage"]].copy()
    df_segment.columns = [
        "seqName",
        f"{segment}_qc.overallScore",
        f"{segment}_qc.overallStatus",
        f"{segment}_coverage"
    ]

    # Add HA-specific fields if they exist
    if segment == "ha":
        if "clade" in df.columns:
            df_segment["ha_clade"] = df["clade"]
        if "subclade" in df.columns:
            df_segment["ha_subclade"] = df["subclade"]
        if "glycosylation" in df.columns:
            df_segment["ha_glycosylation"] = df["glycosylation"]

    # Add NA-specific fields if they exist
    if segment == "na":
        if "glycosylation" in df.columns:
            df_segment["na_glycosylation"] = df["glycosylation"]

    return df_segment

def merge_qc_tables(qc_tables):
    merged = reduce(lambda left, right: pd.merge(left, right, on="seqName"), qc_tables)

    score_cols = [f"{seg}_qc.overallScore" for seg in segments]
    status_cols = [f"{seg}_qc.overallStatus" for seg in segments]
    coverage_cols = [f"{seg}_coverage" for seg in segments]

    # Compute genome-wide scores
    merged["genome_qc.overallScore"] = merged[score_cols].mean(axis=1)
    merged["genome_qc.overallStatus"] = merged.apply(
        lambda row: ";".join(f"{seg}:{row[f'{seg}_qc.overallStatus']}" for seg in segments),
        axis=1
    )

    # NEW: Concatenate coverage values across all segments
    merged["genome_coverage"] = merged.apply(
        lambda row: ";".join(str(row[f"{seg}_coverage"]) for seg in segments),
        axis=1
    )

    return merged

def append_qc_to_metadata(merged_df):
    append_cols = [
        "seqName", "ha_glycosylation", "na_glycosylation",
        "genome_qc.overallScore", "genome_qc.overallStatus",
        "genome_coverage"  # Include new field in metadata # we shold also create a average, minumum 
    ]

    for segment in segments + ["genome"]:
        metadata_path = input_base / segment / "metadata.tsv"
        output_path = input_base / segment / output_metadata_name

        if metadata_path.exists():
            print(f"📝 Updating metadata for {segment}")
            meta_df = pd.read_csv(metadata_path, sep="\t")
            final_df = meta_df.merge(
                merged_df[append_cols],
                left_on="sample_ID",
                right_on="seqName",
                how="left"
            )
            final_df.to_csv(output_path, sep="\t", index=False)
        else:
            print(f"⚠️  Metadata file not found for {segment}: {metadata_path}")

def main():
    qc_tables = []

    for segment in segments:
        run_nextclade(segment)
        qc_data = extract_qc_data(segment)
        qc_tables.append(qc_data)

    merged_qc = merge_qc_tables(qc_tables)

    # Save the genome-wide QC summary
    genome_output = input_base / "genome" / "genome_qc_summary.tsv"
    genome_output.parent.mkdir(parents=True, exist_ok=True)
    merged_qc.to_csv(genome_output, sep="\t", index=False)
    print(f"📁 Saved genome-wide QC summary to {genome_output}")

    append_qc_to_metadata(merged_qc)
    print("🎉 QC pipeline complete.")

if __name__ == "__main__":
    main()