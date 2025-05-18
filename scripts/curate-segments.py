import subprocess
import os

segments = ["pb2", "pb1", "pa", "ha", "np", "na", "mp", "ns", "genome"]
base_metadata = "source/intermediate/vic/ha/metadata_final.tsv"
include_files = [
    "config/vic/include_c3.tsv",
    "config/vic/include_gisaid.tsv",
    "config/vic/include_JHH.tsv",
    "config/vic/include.tsv"
]
exclude = "config/exclude.tsv"

for segment in segments:
    input_fasta = f"source/intermediate/vic/{segment}/sequences.fasta"
    output_dir = f"data/vic/{segment}"
    output_fasta = os.path.join(output_dir, "sequences.fasta")
    output_metadata = os.path.join(output_dir, "metadata.tsv")

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    cmd = [
        "augur", "filter",
        "--metadata", base_metadata,
        "--sequences", input_fasta,
        "--metadata-id-columns", "sample_ID",
        "--exclude-all",
        "--exclude", exclude,
        "--output-sequences", output_fasta,
        "--output-metadata", output_metadata
    ]

    # Add all include files
    for include in include_files:
        cmd.extend(["--include", include])
    
    print(f"Running augur filter for segment: {segment}")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Augur filter failed for segment {segment} with error code {e.returncode}")
